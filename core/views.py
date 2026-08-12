import csv
import io

from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import AnalysisSession, SentimentItem
from .utils import analyze_text

# CONSTANTS
MAX_CSV_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB Max File Size Limit
ITEMS_PER_PAGE = 20  # Rows displayed per table page


def dashboard(request):
    """Renders the dashboard with past analysis sessions."""
    sessions = AnalysisSession.objects.all().order_by('-created_at')
    total_sessions = sessions.count()
    positive_sessions = 0
    negative_sessions = 0
    neutral_sessions = 0

    for session in sessions:
        overall_sentiment = session.overall_sentiment()
        if overall_sentiment == 'positive':
            positive_sessions += 1
        elif overall_sentiment == 'negative':
            negative_sessions += 1
        else:
            neutral_sessions += 1

    context = {
        "sessions": sessions,
        "total_sessions": total_sessions,
        "total_positive_sessions": positive_sessions,
        "total_negative_sessions": negative_sessions,
        "total_neutral_sessions": neutral_sessions,
    }
    return render(request, "dashboard.html", context)


def analyze_single(request):
    """Handles single text input sentiment analysis."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        text = request.POST.get("text", "").strip()

        if not text:
            messages.error(request, "Text input cannot be empty.")
            return redirect("dashboard")
        
        if not title:
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            title = f"Single Text Analysis {timestamp}"

        try:
            session = AnalysisSession.objects.create(title=title)
        except IntegrityError:
            messages.error(
                request,
                f"A session with the title '{title}' already exists. "
                "Please choose a different title.",
            )
            return redirect("dashboard")

        sentiment_score, sentiment_label = analyze_text(text)

        SentimentItem.objects.create(
            session=session,
            content=text,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
        )

        messages.success(request, "Text analyzed successfully!")
        return redirect("session_detail", session_id=session.id)

    return redirect("dashboard")


def analyze_batch(request):
    """Handles CSV upload, validation, encoding recovery, and bulk creation."""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        csv_file = request.FILES.get("csv_file")

        if not title:
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            title = f"Batch CSV Analysis {timestamp}"
        

        # 1. Basic Presence Check
        if not csv_file:
            messages.error(request, "Please select a CSV file to upload.")
            return redirect("dashboard")

        # 2. File Extension Check
        if not csv_file.name.lower().endswith(".csv"):
            messages.error(
                request, "Invalid file format. Please upload a .csv file."
            )
            return redirect("dashboard")

        # 3. File Size Validation
        if csv_file.size > MAX_CSV_SIZE_BYTES:
            messages.error(
                request,
                "File size exceeds the 5 MB limit. Please upload a smaller dataset.",
            )
            return redirect("dashboard")

        # 4. Encoding Recovery & Reading
        try:
            raw_data = csv_file.read()
            if not raw_data:
                messages.error(request, "The uploaded CSV file is empty.")
                return redirect("dashboard")

            # Try utf-8-sig (removes UTF-8 BOM if present from Excel exports)
            try:
                decoded_file = raw_data.decode("utf-8-sig")
            except UnicodeDecodeError:
                # Fallback encoding for legacy CSV formats
                decoded_file = raw_data.decode("latin-1")

            csv_data = io.StringIO(decoded_file)
            reader = csv.DictReader(csv_data)

            if not reader.fieldnames:
                messages.error(
                    request, "The uploaded CSV file has no header row."
                )
                return redirect("dashboard")

            # 5. Dynamic Column Detection
            candidate_columns = [
                "text",
                "comment",
                "tweet",
                "content",
                "review",
                "message",
            ]
            field_map = {
                name.lower().strip(): name
                for name in reader.fieldnames
                if name
            }

            target_column = None
            for candidate in candidate_columns:
                if candidate in field_map:
                    target_column = field_map[candidate]
                    break

            if not target_column:
                messages.error(
                    request,
                    f'CSV must contain one of these columns: {", ".join(candidate_columns)}. '
                    f'Found columns: {", ".join(reader.fieldnames)}',
                )
                return redirect("dashboard")

            try:
                session = AnalysisSession.objects.create(title=title)
            except IntegrityError:
                messages.error(
                    request,
                    f"A session with the title '{title}' already exists. "
                    "Please choose a different title.",
                )
                return redirect("dashboard")

            # 6. Session & Item Generation
            items_to_create = []

            for row in reader:
                text_content = (
                    row.get(target_column, "").strip()
                    if row.get(target_column)
                    else ""
                )
                if text_content:
                    score, label = analyze_text(text_content)
                    items_to_create.append(
                        SentimentItem(
                            session=session,
                            content=text_content,
                            sentiment_score=score,
                            sentiment_label=label,
                        )
                    )

            if not items_to_create:
                session.delete()  # Clean up empty session
                messages.error(
                    request,
                    f'No valid text records found under column "{target_column}".',
                )
                return redirect("dashboard")

            # Batch create in chunks of 500 for high database performance
            SentimentItem.objects.bulk_create(items_to_create, batch_size=500)

            messages.success(
                request,
                f'Successfully processed dataset "{session.title}" '
                f"({len(items_to_create)} items analyzed).",
            )
            return redirect("session_detail", session_id=session.id)

        except Exception as e:
            messages.error(
                request,
                f"An error occurred while processing the file: {str(e)}",
            )
            return redirect("dashboard")

    return redirect("dashboard")


def session_detail(request, session_id):
    """Renders session results with backend SQL pagination."""
    session = get_object_or_404(AnalysisSession, id=session_id)
    items_list = session.items.all()

    # 7. Django Backend Pagination
    paginator = Paginator(items_list, ITEMS_PER_PAGE)
    page_number = request.GET.get("page", 1)

    try:
        items = paginator.page(page_number)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    return render(
        request, "session_detail.html", {"session": session, "items": items}
    )

def export_session_csv(request, session_id):
    """Generates and downloads a CSV report of the analysis session."""
    session = get_object_or_404(AnalysisSession, id=session_id)
    response = HttpResponse(content_type='text/csv')
    
    safe_title = session.title.replace(' ', '_').replace('/', '-')
    response['Content-Disposition'] = f'attachment; filename="SentiMetrics_Report_{safe_title}.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['Text Content', 'Sentiment Score', 'Sentiment Label', 'Analyzed At'])
    
    for item in session.items.all().iterator():
        writer.writerow([
            item.content, 
            item.sentiment_score, 
            item.sentiment_label, 
            item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    return response