import csv
import io

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .models import AnalysisSession, SentimentItem
from .utils import analyze_text


def dashboard(request):
    """Renders the dashboard page."""
    try:
        sessions = AnalysisSession.objects.all()
        return render(request, 'dashboard.html', {'sessions': sessions})
    except Exception as e:
        messages.error(request, f"Error occurred while fetching sessions: {e}")
        return render(request, 'dashboard.html', {'sessions': []})

def analyze_single(request):
    """Handles single text sentiment analysis."""
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Session').strip()
        text = request.POST.get('text', '').strip()

        try:
            if not title:
                messages.error(request, "Title cannot be empty.")
                return redirect('dashboard')

            if text:
                session = AnalysisSession.objects.create(title=title)
                score, sentiment = analyze_text(text)

                # FIX 1: Changed `text=text` to `content=text` to match models.py
                SentimentItem.objects.create(
                    session=session,
                    content=text,  
                    sentiment_score=score,
                    sentiment_label=sentiment
                )

                messages.success(request, f"Analysis complete! Sentiment: {sentiment}")
                # FIX 2: Redirect to session_detail, not dashboard
                return redirect('session_detail', session_id=session.id)
            else:
                messages.error(request, "Text content cannot be empty.")
                return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Error occurred during analysis: {e}")
            return redirect('dashboard')
            
    return redirect('dashboard')

def analyze_batch(request):
    """Handles batch sentiment analysis via CSV upload."""
    if request.method == 'POST':
        title = request.POST.get('title', 'Untitled Batch Session').strip()
        csv_file = request.FILES.get('csv_file')

        # FIX 3: Changed 'and' to 'or' to prevent AttributeError if file is missing
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect('dashboard')

        try:
            file_data = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(file_data))
            
            header = next(csv_reader)
            text_col_index = 0

            keywords = ['text', 'comment', 'tweet', 'review', 'content']
            for i, col_name in enumerate(header):
                col_lower = col_name.lower()
                if any(keyword in col_lower for keyword in keywords):
                    text_col_index = i
                    break

            session = AnalysisSession.objects.create(title=title)
            items_to_create = []

            for row in csv_reader:
                if len(row) > text_col_index:
                    content = row[text_col_index].strip()
                    if content:
                        score, label = analyze_text(content)
                        items_to_create.append(
                            SentimentItem(
                                session=session,
                                content=content,
                                sentiment_score=score,
                                sentiment_label=label
                            )
                        )

            SentimentItem.objects.bulk_create(items_to_create)
            
            messages.success(request, f"Successfully analyzed {len(items_to_create)} rows!")
            return redirect('session_detail', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
            return redirect('dashboard')

    return redirect('dashboard')

def session_detail(request, session_id):
    """Displays the detailed charts and table for a specific session."""
    session = get_object_or_404(AnalysisSession, id=session_id)
    items = session.items.all()
    
    context = {
        'session': session,
        'items': items,
    }
    return render(request, 'session_detail.html', context)