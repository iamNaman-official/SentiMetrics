from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_text(text: str) -> tuple[float, str]:
    """
    Analyze the sentiment of the given text using VADER sentiment analysis.

    Args:
        text (str): The input text to analyze.

    Returns:
        tuple: A tuple containing (compound_score, sentiment_label).
    """
    try:
        # 1. Check for empty or invalid input
        if not text or not isinstance(text, str):
            return 0.0, 'neutral'

        # 2. Analyze the text (Now safely inside the try block)
        scores = analyzer.polarity_scores(text)
        compound_score = scores['compound']

        # 3. Classify based on standard VADER thresholds
        if compound_score >= 0.05:
            sentiment = 'positive'
        elif compound_score <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
            
        return compound_score, sentiment

    except Exception as e:
        print(f"Error occurred while analyzing sentiment: {e}")
        return 0.0, 'neutral'