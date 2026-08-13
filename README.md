# SentiMetrics

> **From raw feedback to actionable sentiment intelligence.**

SentiMetrics is a web-based sentiment analytics platform built with **Django, Python, VADER Sentiment Analysis, and local AI through Ollama**.

It allows users to analyze individual text or process entire CSV datasets, classify feedback into positive, negative, and neutral sentiment, visualize sentiment distributions, identify frequently occurring negative terms, and generate an AI-powered executive summary from the analyzed feedback.

The goal is simple:

> **Turn large amounts of unstructured textual feedback into structured insights that are easier to understand and act upon.**

---

##  What Problem Does SentiMetrics Solve?

Businesses, researchers, product teams, and organizations collect large amounts of textual feedback through:

* Customer reviews
* Product feedback
* Support tickets
* Survey responses
* Social media comments
* App reviews
* Tweets
* Online discussions

The problem is that raw feedback is difficult to interpret at scale.

Reading hundreds or thousands of comments manually is:

* Time-consuming
* Difficult to scale
* Inconsistent
* Hard to summarize
* Difficult to convert into actionable insights

SentiMetrics automates the first stage of this process.

Instead of manually going through every response, users can upload their feedback and receive:

```text
Raw Feedback
      ↓
Data Validation
      ↓
Sentiment Analysis
      ↓
Positive / Neutral / Negative
      ↓
Statistical Summary
      ↓
Visual Analytics
      ↓
Negative-Term Analysis
      ↓
Local AI Executive Summary
      ↓
Exportable Results
```

---

#  Core Idea

Most basic sentiment-analysis applications stop at:

> "This text is positive."

SentiMetrics goes further by organizing the analysis into a complete workflow.

It provides:

* Sentiment classification
* Sentiment scores
* Dataset-level statistics
* Average sentiment score
* Dominant sentiment detection
* Sentiment distribution visualization
* Negative-word analysis
* Search and sentiment filtering
* Historical analysis sessions
* CSV report export
* Local AI-generated executive summaries

This allows users to move from **classification → analysis → interpretation**.

---

#  Key Features

## 1. Single Text Sentiment Analysis

Analyze an individual piece of text directly from the dashboard.

Example:

```text
Input:
"The new update is amazing and much faster."

Output:
Sentiment: Positive
Compound Score: Positive
```

Users can optionally provide a custom analysis-session title.

If no title is provided, SentiMetrics automatically generates one using the current timestamp.

---

## 2. Batch CSV Sentiment Analysis

Users can upload a CSV dataset and analyze multiple feedback records at once.

Example:

```csv
review
"The product is excellent."
"The delivery was terrible."
"The experience was average."
```

SentiMetrics processes the records and creates a persistent analysis session containing the results.

---

## 3. Automatic Text-Column Detection

SentiMetrics does not require every dataset to use the exact same column name.

The application searches for supported text columns including:

```text
text
comment
tweet
content
review
message
```

The first matching column is automatically selected for analysis.

This allows datasets from different sources to be processed without manually renaming their columns.

---

## 4. CSV Validation

Uploaded datasets are validated before processing.

The application checks:

* Whether a file was uploaded
* Whether the file is a `.csv`
* Whether the file is empty
* Whether the file exceeds the size limit
* Whether a header row exists
* Whether a supported text column exists

The current maximum CSV upload size is:

```text
5 MB
```

---

## 5. Encoding Recovery

SentiMetrics first attempts to decode uploaded CSV files using:

```text
UTF-8 with BOM support
```

If UTF-8 decoding fails, the application falls back to:

```text
Latin-1
```

This improves compatibility with CSV files exported by different applications and older systems.

---

#  Sentiment Analysis Engine

SentiMetrics currently uses:

**VADER — Valence Aware Dictionary and sEntiment Reasoner**

VADER is a lightweight lexicon- and rule-based sentiment analysis system designed particularly for text such as social media and short-form feedback.

The project extracts VADER's compound sentiment score and maps it to one of three categories.

### Score range

```text
-1.0 ───────────────────────────── +1.0
Negative                           Positive
```

### Classification

```text
Compound Score >= 0.05
        ↓
     POSITIVE

Compound Score <= -0.05
        ↓
     NEGATIVE

Between -0.05 and +0.05
        ↓
     NEUTRAL
```

The thresholds follow the standard VADER sentiment classification approach.

---

#  Analytics Dashboard

Each completed analysis session provides dataset-level statistics.

## Total Analyzed

Shows the number of valid feedback items processed.

## Average Sentiment Score

Calculates the average compound sentiment score across the session.

This gives a high-level indication of the overall sentiment direction.

## Dominant Sentiment

Determines whether the largest proportion of analyzed feedback is:

```text
Positive
Negative
Neutral
```

---

#  Sentiment Distribution

SentiMetrics visualizes the distribution of:

* Positive feedback
* Negative feedback
* Neutral feedback

The current interface uses a doughnut chart to make the distribution easier to understand at a glance.

Example:

```text
Positive     62%
Neutral      14%
Negative     24%
```

The exact values depend on the uploaded dataset.

---

#  Negative Word Cloud

SentiMetrics includes a negative-feedback word cloud.

The system:

1. Identifies currently visible negative feedback.
2. Extracts words from those records.
3. Removes common stop words.
4. Counts word frequency.
5. Displays the most frequent terms visually.

Up to the top 35 words are displayed.

This helps users quickly identify recurring vocabulary within negative feedback.

For example:

```text
       battery

  slow        expensive

       support

   broken       delivery
```

The word cloud is interactive.

Clicking a word applies it as a search filter to the analyzed feedback table.

---

#  Search and Sentiment Filtering

The analyzed-items section provides:

### Text Search

Users can search through analyzed comments.

### Sentiment Filters

Users can filter the dataset by:

```text
All
Positive
Negative
Neutral
```

This makes it easier to isolate specific categories of feedback.

For example:

> Search for `battery` + filter `Negative`

can quickly surface negative feedback related to battery problems.

---

#  Local AI Executive Summary

One of the major additions to the current version of SentiMetrics is a **local AI-powered executive summary**.

Instead of forcing users to manually interpret all the individual sentiment results, SentiMetrics can generate a concise summary of the feedback landscape.

The system:

1. Retrieves a balanced sample of positive, negative, and neutral feedback.
2. Sends the selected feedback to a locally running Ollama model.
3. Uses the model to generate an executive-style summary.
4. Displays the generated summary inside the analysis page.

The summary is instructed to focus on:

* Overall sentiment trends
* Strengths
* Pain points
* Important feedback patterns

---

#  Why Local AI?

The AI summary uses a **locally running Ollama instance** instead of sending feedback to an external cloud AI API.

This provides an important privacy advantage for sensitive feedback datasets because the AI processing can remain on the user's machine.

Current implementation:

```text
SentiMetrics
     │
     ▼
Django Backend
     │
     ▼
Local Ollama API
     │
     ▼
Local Language Model
     │
     ▼
Executive Summary
```

The current implementation uses:

```text
qwen2.5-coder:7b
```

as the configured Ollama model.

---

#  Why Use Two Different AI/NLP Components?

SentiMetrics deliberately separates:

### Sentiment classification

**VADER**

Used for:

```text
Text
 ↓
Sentiment Score
 ↓
Positive / Negative / Neutral
```

### Higher-level interpretation

**Local Ollama model**

Used for:

```text
Sampled Feedback
 ↓
Pattern Interpretation
 ↓
Executive Summary
```

This separation allows the application to use a lightweight deterministic sentiment engine for classification while using a local language model for higher-level interpretation.

---

#  Batch Processing Optimization

CSV processing is designed to avoid creating database records one at a time.

After sentiment analysis, results are inserted using:

```python
bulk_create(..., batch_size=500)
```

This allows database insertion to occur in batches rather than performing a separate database operation for every analyzed item.

The current implementation uses a batch size of:

```text
500 records
```

---

#  Analysis Sessions

Every analysis is stored as an `AnalysisSession`.

A session contains:

* Session title
* Creation timestamp
* Analyzed feedback items
* Sentiment scores
* Sentiment classifications

This allows users to maintain a history of different datasets and analyses.

Example:

```text
Customer Reviews – July
App Store Reviews
Support Tickets – Q3
Product Feedback
Social Media Dataset
```

---

#  Database Structure

SentiMetrics currently uses two primary data models.

## AnalysisSession

Represents a complete analysis.

```text
AnalysisSession
├── title
├── created_at
└── sentiment items
```

## SentimentItem

Represents an individual analyzed text record.

```text
SentimentItem
├── session
├── content
├── sentiment_score
├── sentiment_label
└── created_at
```

Database indexes are also used on:

```text
session + created_at
sentiment_label
```

to improve query efficiency for common operations.

---

#  CSV Export

Completed analysis sessions can be exported as CSV reports.

The exported report contains:

```text
Text Content
Sentiment Score
Sentiment Label
Analyzed At
```

Example:

```csv
Text Content,Sentiment Score,Sentiment Label,Analyzed At
"The product is excellent",0.5719,positive,2026-08-13 10:20:00
"The service was terrible",-0.4767,negative,2026-08-13 10:21:00
"The product is okay",0.2263,positive,2026-08-13 10:22:00
```

---

#  System Architecture

```text
                         ┌───────────────────┐
                         │       USER        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Django Web UI   │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Single Text      │          │ CSV Batch        │
          │ Analysis         │          │ Upload           │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Input Validation    │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ VADER Sentiment     │
                       │ Analysis             │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Score + Label       │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Django Database     │
                       └──────────┬──────────┘
                                  │
                     ┌────────────┴─────────────┐
                     │                          │
                     ▼                          ▼
          ┌────────────────────┐      ┌────────────────────┐
          │ Statistical        │      │ Visualization      │
          │ Analytics          │      │ & Word Cloud       │
          └────────────────────┘      └────────────────────┘
                     │
                     ▼
          ┌────────────────────┐
          │ Local Ollama AI    │
          │ Executive Summary  │
          └─────────┬──────────┘
                    ▼
          ┌────────────────────┐
          │ Actionable         │
          │ Feedback Insights  │
          └────────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

* Python
* Django 6.1

## NLP / Sentiment Analysis

* VADER Sentiment 3.3.2

## Local AI

* Ollama
* Qwen 2.5 Coder 7B

## Data Processing

* Pandas
* NumPy
* Python CSV utilities

## Database

* Django ORM
* SQLite / Django-supported database configuration

## Frontend

* Django Templates
* HTML
* JavaScript
* Tailwind-style utility classes

## Visualization

* Chart.js
* WordCloud2.js

## Reporting

* CSV export
* ReportLab dependency

## Development / Code Quality

* Ruff

---

#  Project Structure

```text
SentiMetrics/
│
├── .github/
│   └── workflows/
│
├── core/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
│
├── sentimetrics_proj/
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── session_detail.html
│
├── .gitignore
├── .hintrc
├── manage.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── sentiment_data.csv
```

---

#  End-to-End Workflow

### Single Text

```text
User enters text
      ↓
Django receives request
      ↓
Input validation
      ↓
VADER analysis
      ↓
Compound score
      ↓
Sentiment classification
      ↓
Database storage
      ↓
Results dashboard
```

### CSV Dataset

```text
Upload CSV
    ↓
Validate file
    ↓
Check file size
    ↓
Decode CSV
    ↓
Detect text column
    ↓
Read valid records
    ↓
Run VADER
    ↓
Bulk database insertion
    ↓
Generate analytics
    ↓
Display results
```

### AI Insights

```text
Stored feedback
      ↓
Balanced sampling
      ↓
Positive + Negative + Neutral samples
      ↓
Local Ollama API
      ↓
Qwen model
      ↓
Executive summary
```
---

#  Using SentiMetrics

## Analyze Individual Text

1. Open the dashboard.
2. Enter an optional session title.
3. Paste your text.
4. Click **Analyze Sentiment**.
5. Open the generated session.
6. Review the sentiment score and classification.

---

## Analyze a CSV

1. Prepare a CSV file.
2. Make sure it contains a supported text column.
3. Open the dashboard.
4. Select the CSV file.
5. Optionally enter a session title.
6. Click **Process Batch**.
7. Review the generated analysis.
8. Use the dashboard filters and analytics.
9. Export the results if required.

---

#  Supported CSV Columns

SentiMetrics currently recognizes:

```text
text
comment
tweet
content
review
message
```

Example:

```csv
text
"I love the new product."
"The application keeps crashing."
"The experience was okay."
```

---

#  Example Analysis

Input:

```text
"The camera quality is excellent, but the battery life is disappointing."
```

SentiMetrics processes the text using VADER and produces:

```text
Sentiment Score
       ↓
Compound Score

Sentiment
       ↓
Positive / Negative / Neutral
```

For a larger dataset, the session additionally provides:

```text
Total Analyzed
Average Score
Dominant Sentiment
Sentiment Distribution
Negative Word Cloud
Search & Filtering
AI Executive Summary
```

---

#  What Makes SentiMetrics Different?

The sentiment-analysis algorithm itself is not claimed to be novel.

The focus of SentiMetrics is the **complete analysis workflow**.

Instead of only answering:

> "Is this text positive or negative?"

SentiMetrics combines:

```text
Classification
      +
Dataset Analytics
      +
Visualization
      +
Negative-Term Discovery
      +
Local AI Interpretation
      +
Exportable Results
```

This creates a bridge between **raw textual feedback** and **human-readable insights**.

The local AI layer is particularly useful because it can interpret a balanced sample of the analyzed feedback without requiring that feedback to be sent to a third-party cloud AI service.

---

#  Limitations

SentiMetrics currently has several known limitations.

## VADER Context

VADER is not a large contextual language model.

It may struggle with:

* Sarcasm
* Complex context
* Domain-specific terminology
* Ambiguous statements
* Long contextual dependencies
* Mixed sentiment
* Code-mixed language

Example:

```text
"Great, another update that broke everything."
```

The intended sentiment is negative, but the word "Great" is literally positive.

---

## Local AI Dependency

The AI Executive Summary requires:

* Ollama to be installed
* Ollama to be running
* The configured model to be available

If Ollama is unavailable, SentiMetrics falls back to a deterministic summary based on sentiment counts rather than failing the entire analysis.

---

## CSV Size

The current upload limit is:

```text
5 MB
```

This is appropriate for the current prototype but is not intended to represent a production-scale data-processing limit.

---

## No Formal Accuracy Claim

SentiMetrics does not currently claim a specific sentiment-analysis accuracy percentage.

A formal evaluation would require testing against a labeled benchmark or domain-specific validation dataset.

---

#  Future Improvements

Potential future development includes:

### NLP

* Transformer-based sentiment models
* Context-aware sentiment classification
* Aspect-based sentiment analysis
* Sarcasm detection
* Multilingual sentiment analysis
* Hindi / Hinglish support

### Analytics

* Sentiment trends over time
* Topic extraction
* Aspect-level sentiment
* Automated issue detection
* Emerging complaint detection
* Comparative dataset analysis
* Customer-segment analysis

### AI

* More capable local language models
* Configurable AI models
* Evidence-backed AI insights
* AI-generated recommendations
* Automatic root-cause analysis

### Scalability

* Background task processing
* Larger dataset support
* Chunked file processing
* Redis / Celery integration
* Cloud deployment
* API access

### Product

* User authentication
* Multi-user workspaces
* Saved dashboards
* PDF reports
* Scheduled analysis
* REST API
* External data-source integrations

---

#  Hackathon Vision

SentiMetrics is designed around a simple progression:

```text
RAW FEEDBACK
     ↓
UNDERSTAND SENTIMENT
     ↓
IDENTIFY PATTERNS
     ↓
UNDERSTAND PAIN POINTS
     ↓
GENERATE INSIGHTS
     ↓
MAKE BETTER DECISIONS
```

The long-term vision is to evolve SentiMetrics from a **sentiment-analysis application** into a broader **feedback intelligence platform**.

---

#  Team

SentiMetrics is being developed as a team project for a hackathon.

| Member        | Role      | Contribution     |
| ------------- | --------- | ---------------- |
| Team Member 1 | Developer | Add contribution |
| Team Member 2 | Developer | Add contribution |
| Team Member 3 | Developer | Add contribution |
| Team Member 4 | Developer | Add contribution |

---

#  Project Status

**Current Status: Hackathon Prototype**

Implemented:

* [x] Single-text sentiment analysis
* [x] CSV batch processing
* [x] CSV validation
* [x] Dynamic text-column detection
* [x] UTF-8 / Latin-1 encoding recovery
* [x] VADER sentiment scoring
* [x] Positive / negative / neutral classification
* [x] Persistent analysis sessions
* [x] Average sentiment scoring
* [x] Dominant sentiment detection
* [x] Sentiment distribution visualization
* [x] Negative-word cloud
* [x] Search and sentiment filtering
* [x] CSV report export
* [x] Local Ollama AI executive summaries
* [x] Fallback summary when Ollama is unavailable
* [x] Batch database insertion optimization

---

#  License

MIT License.

---

# 🔗 Repository

**SentiMetrics**

GitHub:

https://github.com/iamNaman-official/SentiMetrics

---

> **SentiMetrics — Turn feedback into insight.**
