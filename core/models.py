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

    @property
    def generate_insights(self):
        """Generate a concise executive summary using a local Ollama model."""
        from collections import Counter

        import requests

        total_items = self.items.count()

        if total_items == 0:
            return "No items found in this session to analyze."

        # Fetch a balanced sample
        positive_samples = list(
            self.items.filter(sentiment_label="positive")
            .values_list("content", flat=True)[:15]
        )

        negative_samples = list(
            self.items.filter(sentiment_label="negative")
            .values_list("content", flat=True)[:15]
        )

        neutral_samples = list(
            self.items.filter(sentiment_label="neutral")
            .values_list("content", flat=True)[:10]
        )

        samples = positive_samples + negative_samples + neutral_samples

        if not samples:
            return "Not enough data points available for an executive summary."

        feedback_text = "\n".join(f"- {text}" for text in samples)

        prompt = f"""
        You are a senior product analyst preparing an executive summary for leadership.

        Analyze the following user feedback samples and write exactly **three professional sentences**.

        Requirements:
        - Focus on overall sentiment trends.
        - Mention both strengths and pain points if they exist.
        - Do not mention percentages unless explicitly evident.
        - Return only the final paragraph with no markdown or code.

        Feedback:
        {feedback_text}
        """

        try:
            # Direct HTTP call to local Ollama server API
            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "qwen2.5-coder:7b",  # Matches your installed model list
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": 8192,
                        "temperature": 0.3,
                    },
                },
                timeout=120,
            )

            response.raise_for_status()
            summary = response.json().get("response", "").strip()

            # Remove accidental markdown fences
            for token in ("```python", "```", "```output"):
                summary = summary.replace(token, "")

            if summary:
                return summary.strip()

        except Exception as e:
            print(f"Ollama error: {e}")

        # Fallback block if Ollama connection fails
        sentiment_counts = Counter(
            self.items.values_list("sentiment_label", flat=True)
        )

        positive = sentiment_counts.get("positive", 0)
        negative = sentiment_counts.get("negative", 0)
        neutral = sentiment_counts.get("neutral", 0)

        dominant = max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else "neutral"

        return (
            f"Analysis covered {total_items} feedback items, with {dominant} sentiment being the most common. "
            f"The dataset contains {positive} positive, {negative} negative, and {neutral} neutral responses. "
            "Positive themes indicate user satisfaction, while recurring negative feedback suggests areas that warrant product and workflow improvements."
        )



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
        """Returns string representation for admin and debugging."""
        return f"{self.sentiment_label}: {self.content[:50]}..."