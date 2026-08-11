from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import AnalysisSession, SentimentItem
from .utils import analyze_text


class NLPUtilsTests(TestCase):
    """Tests the underlying VADER sentiment engine."""
    
    def test_analyze_positive_text(self):
        score, label = analyze_text("I absolutely love this! It is fantastic.")
        self.assertEqual(label, "positive")
        self.assertGreater(score, 0.5)

    def test_analyze_negative_text(self):
        score, label = analyze_text("This is the worst experience ever. Terrible.")
        self.assertEqual(label, "negative")
        self.assertLess(score, -0.5)

    def test_analyze_neutral_text(self):
        score, label = analyze_text("The package arrived on Tuesday.")
        self.assertEqual(label, "neutral")
        self.assertEqual(score, 0.0)

    def test_analyze_empty_text(self):
        score, label = analyze_text("   ")
        self.assertEqual(label, "neutral")
        self.assertEqual(score, 0.0)


class DatabaseModelTests(TestCase):
    """Tests the 'Fat Model' methods on the AnalysisSession database model."""
    
    def setUp(self):
        # This runs before every test to set up mock data
        self.session = AnalysisSession.objects.create(title="Test Session")
        
        # Create 2 positive, 1 negative, and 1 neutral item (Total: 4 items)
        SentimentItem.objects.create(
            session=self.session,
            content="Good",
            sentiment_score=0.8,
            sentiment_label="positive",
        )
        SentimentItem.objects.create(
            session=self.session,
            content="Great",
            sentiment_score=0.9,
            sentiment_label="positive",
        )
        SentimentItem.objects.create(
            session=self.session,
            content="Bad",
            sentiment_score=-0.5,
            sentiment_label="negative",
        )
        SentimentItem.objects.create(
            session=self.session,
            content="Okay",
            sentiment_score=0.0,
            sentiment_label="neutral",
        )

    def test_total_items(self):
        self.assertEqual(self.session.total_items(), 4)

    def test_average_sentiment_score(self):
        # (0.8 + 0.9 - 0.5 + 0.0) / 4 = 1.2 / 4 = 0.3
        self.assertAlmostEqual(self.session.average_sentiment_score(), 0.3)

    def test_overall_sentiment(self):
        # 50% positive, 25% negative, 25% neutral -> Positive wins
        self.assertEqual(self.session.overall_sentiment(), "positive")

    def test_chart_data_structure(self):
        data = self.session.chart_data()
        self.assertIn("labels", data)
        self.assertIn("counts", data)
        # 2 positive, 1 negative, 1 neutral
        self.assertEqual(data["counts"], [2, 1, 1])


class ViewIntegrationTests(TestCase):
    """Tests the routing, views, form submissions, and file uploads."""
    
    def setUp(self):
        self.client = Client()
        self.session = AnalysisSession.objects.create(title="Existing Session")

    def test_dashboard_loads(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_analyze_single_valid_submission(self):
        response = self.client.post(reverse("analyze_single"), {
            "title": "Single Test",
            "text": "I am very happy with this product."
        })
        # Check if it created the session successfully in the DB
        self.assertTrue(AnalysisSession.objects.filter(title="Single Test").exists())
        # Check if it redirected to the detail page (status 302)
        new_session = AnalysisSession.objects.get(title="Single Test")
        self.assertRedirects(response, reverse("session_detail", args=[new_session.id]))

    def test_analyze_single_empty_text(self):
        # Should reject empty text and redirect back to dashboard
        response = self.client.post(reverse("analyze_single"), {
            "text": "   "
        })
        self.assertRedirects(response, reverse("dashboard"))

    def test_analyze_batch_csv_upload(self):
        # Mocking a CSV file upload directly in Python memory
        csv_content = b"text\nI love this product\nI hate this product\n"
        csv_file = SimpleUploadedFile("test_data.csv", csv_content, content_type="text/csv")
        
        response = self.client.post(reverse("analyze_batch"), {
            "title": "Mock CSV Upload",
            "csv_file": csv_file
        })
        
        new_session = AnalysisSession.objects.get(title="Mock CSV Upload")
        self.assertEqual(new_session.items.count(), 2)
        self.assertRedirects(response, reverse("session_detail", args=[new_session.id]))

    def test_csv_export_endpoint(self):
        # Create a mock item to test the download
        SentimentItem.objects.create(
            session=self.session,
            content="Download test",
            sentiment_score=0.9,
            sentiment_label="positive",
        )
        
        response = self.client.get(reverse("export_session_csv", args=[self.session.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(b"Download test", response.content)  # Ensure text is in the CSV