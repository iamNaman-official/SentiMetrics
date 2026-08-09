from django.db import models
from django.db.models import Avg

class AnalysisSession(models.Model):
    """Represents a single analysis session, which can contain multiple sentiment items."""
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] 
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_session_title')
        ]

    def __str__(self) -> str:
        """String representation of the session, primarily for admin and debugging purposes."""
        return self.title

    def total_items(self) -> int:
        """Returns the dynamic count of items in this session."""
        return self.items.count()

    def sentiment_percentage(self) -> dict[str, float]:
        """Calculates percentage breakdown for each sentiment category."""
        total = self.total_items()
        if total == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}

        positive_count = self.items.filter(sentiment_label='positive').count()
        negative_count = self.items.filter(sentiment_label='negative').count()
        neutral_count = self.items.filter(sentiment_label='neutral').count()

        return {
            'positive': round((positive_count / total) * 100, 2),
            'negative': round((negative_count / total) * 100, 2),
            'neutral': round((neutral_count / total) * 100, 2),
        }

    def average_sentiment_score(self) -> float:
        """Calculates average sentiment score at database level."""
        result = self.items.aggregate(avg_score=Avg('sentiment_score'))['avg_score']
        return round(result, 3) if result is not None else 0.0

    def overall_sentiment(self) -> str:
        """Determines the dominant sentiment category."""
        percentages = self.sentiment_percentage()
        if sum(percentages.values()) == 0:
            return 'neutral'

        return max(percentages, key=percentages.get)

    def chart_data(self) -> dict:
        """Formats data structure directly for Chart.js on the frontend."""
        return {
            'labels': ['Positive', 'Negative', 'Neutral'],
            'counts': [
                self.items.filter(sentiment_label='positive').count(),
                self.items.filter(sentiment_label='negative').count(),
                self.items.filter(sentiment_label='neutral').count()
            ],
            'colors': ['#28a745', '#dc3545', '#ffc107']  # Clean Bootstrap Green, Red, Yellow
        }


class SentimentItem(models.Model):
    """Represents a single sentiment analysis item, linked to an AnalysisSession."""
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='items')
    content = models.TextField()
    sentiment_score = models.FloatField() 
    sentiment_label = models.CharField(max_length=10) # Stores 'positive', 'negative', or 'neutral'
    created_at = models.DateTimeField(auto_now_add=True)  # Added missing field

    class Meta:
        ordering = ['created_at']
        indexes = [  # Moved from constraints to indexes
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['sentiment_label']),
        ]

    def __str__(self) -> str:
        """String representation of the sentiment item, primarily for admin and debugging purposes."""
        return f"{self.sentiment_label}: {self.content[:50]}..."