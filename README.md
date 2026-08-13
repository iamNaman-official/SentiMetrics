# SentiMetrics

> **A practical sentiment analysis platform for analyzing individual text and large collections of text through CSV datasets.**

SentiMetrics is a web-based sentiment analysis application built with **Django and Python**. It allows users to analyze individual pieces of text or process an entire CSV dataset and classify each entry as **Positive, Negative, or Neutral** using the **VADER Sentiment Analysis** engine.

The application is designed to make sentiment analysis simple, fast, and accessible through a clean web interface while maintaining analysis sessions and allowing processed results to be exported as CSV reports.

---
## Overview

Understanding what people think about a product, service, topic, event, or piece of content can be difficult when the amount of feedback becomes large.

Manually reading hundreds or thousands of comments and reviews is time-consuming and makes it difficult to identify overall sentiment patterns.

**SentiMetrics** addresses this problem by providing a web-based interface where users can:

1. Enter a single piece of text for immediate sentiment analysis.
2. Upload a CSV dataset containing multiple text records.
3. Automatically analyze each valid text entry.
4. Classify the entries as positive, negative, or neutral.
5. Review previous analysis sessions.
6. Browse results through paginated tables.
7. Export processed results as a CSV report.

---

## Problem Statement

Organizations, researchers, developers, and individuals frequently collect textual feedback from sources such as:

* Product reviews
* Customer feedback
* Social media posts
* Survey responses
* Comments
* Tweets
* Messages
* Online discussions

The problem is that raw text data does not immediately provide actionable insight.

For example:

> "The product looks amazing, but the battery life is disappointing."

A human can understand the overall sentiment, but analyzing thousands of similar responses manually is inefficient.

SentiMetrics provides an automated approach for converting textual feedback into structured sentiment information.

---

## Solution

SentiMetrics processes textual input through a sentiment analysis pipeline.

### Basic workflow

```
User Input / CSV Dataset
          │
          ▼
    Input Validation
          │
          ▼
    Text Extraction
          │
          ▼
   VADER Sentiment Analysis
          │
          ▼
   Compound Sentiment Score
          │
          ▼
 Positive / Neutral / Negative
          │
          ▼
 Database Storage
          │
          ▼
 Results Dashboard
          │
          ▼
      CSV Export
```

The application supports both **single-text analysis** and **batch dataset processing**.

---

# Key Features

## 1. Single Text Analysis

Users can enter an individual sentence, review, comment, tweet, or other text and analyze its sentiment.

Example:

```
Input:
"The new update is fantastic and much faster than the previous version."

Output:
Sentiment: Positive
```

A session can also be given a custom title for easier identification later.

---

## 2. Batch CSV Sentiment Analysis

SentiMetrics can process multiple text records from a CSV file.

Instead of analyzing every entry individually, users can upload a dataset and process the records in bulk.

Example dataset:

| text                      |
| ------------------------- |
| The product is excellent. |
| The service was terrible. |
| The experience was okay.  |

The system analyzes each record and stores its sentiment result.

---

## 3. VADER Sentiment Analysis

SentiMetrics uses **VADER (Valence Aware Dictionary and sEntiment Reasoner)** for sentiment analysis.

The system extracts the VADER compound score and maps it to a sentiment label.

### Classification thresholds

|         Compound Score | Classification |
| ---------------------: | -------------- |
|              `>= 0.05` | Positive       |
| `-0.05 < score < 0.05` | Neutral        |
|             `<= -0.05` | Negative       |

This classification logic is implemented directly in the project's sentiment-analysis utility.

---

## 4. Analysis Sessions

Each analysis is organized into a session.

Sessions allow users to keep track of different analyses instead of treating every result as an isolated calculation.

For example:

```
iPhone 15 Reviews
Customer Feedback – July
Twitter Dataset
Product Survey
```

---

## 5. Historical Results

Previously processed sessions are displayed on the dashboard.

Users can select a session and view its associated sentiment-analysis results.

---

## 6. Paginated Results

Large datasets can contain many records.

To prevent all records from being displayed at once, SentiMetrics uses backend pagination.

The current implementation displays:

```
20 records per page
```

This keeps result pages manageable even when processing larger datasets.

---

## 7. CSV Report Export

Processed analysis sessions can be exported as CSV reports.

The generated report contains:

* Original text
* Sentiment score
* Sentiment label
* Analysis timestamp

Example:
36
```
Text Content,Sentiment Score,Sentiment Label,Analyzed At
"The product is excellent",0.5719,positive,2026-08-12 12:00:00
"The service was terrible",-0.4767,negative,2026-08-12 12:01:00
```

---

## 8. CSV Validation

Before processing a dataset, SentiMetrics validates the uploaded file.

The application checks:

* File presence
* `.csv` extension
* File size
* Empty files
* CSV header availability
* Supported text columns

The maximum CSV upload size is currently:

```
5 MB
```

---

## 9. Flexible Text Column Detection

The application does not require only one specific column name.

It searches for supported text-related column names including:

```
text
comment
tweet
content
review
message
```

This makes the system easier to use with datasets from different sources.

---

## 10. Encoding Recovery

SentiMetrics first attempts to decode uploaded CSV files using UTF-8 with BOM handling.

If that fails, it falls back to Latin-1 decoding.

This helps the application handle CSV files originating from different tools and legacy datasets.

---

# How It Works

SentiMetrics follows a simple processing pipeline.

### Step 1 — Input

The user provides either:

* A single text input
* A CSV dataset

### Step 2 — Validation

The application validates the input before processing it.

For CSV files, it verifies the file format, file size, header row, and supported text column.

### Step 3 — Text Extraction

The relevant text is extracted from the input.

For batch processing, the application automatically identifies a supported text column.

### Step 4 — Sentiment Analysis

Each text entry is passed to the VADER sentiment analyzer.

The analyzer produces sentiment scores, including the compound score.

### Step 5 — Classification

The compound score is converted into one of three categories:

```
Positive
Neutral
Negative
```

### Step 6 — Storage

The analysis session and individual sentiment results are stored in the application's database.

### Step 7 — Presentation

The user can view the processed results through the web interface.

### Step 8 — Export

The complete session can be exported as a CSV report.

---

# Technology Stack

## Backend

* Python
* Django

## Sentiment Analysis

* VADER Sentiment

## Data Processing

* Pandas
* NumPy
* Python CSV utilities

## Database / ORM

* Django ORM

## Frontend

* HTML
* Django Templates
* Bootstrap-based UI

## Reporting

* CSV export
* ReportLab dependency included for report-generation capabilities

## Development / Code Quality

* Ruff

---

# System Architecture

```
                    ┌──────────────────────┐
                    │       User           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Django Web UI      │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ Single Text     │       │ CSV Upload      │
        │ Analysis        │       │ Processing      │
        └────────┬────────┘       └────────┬────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                  ┌──────────────────────┐
                  │ Input Validation     │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ VADER Analyzer       │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ Sentiment Score      │
                  │ + Classification     │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ Django Database      │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ Results Dashboard    │
                  └──────────┬───────────┘
                             ▼
                  ┌──────────────────────┐
                  │ CSV Report Export    │
                  └──────────────────────┘
```

---

# Project Structure

```
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
├── readme.md
├── requirements.txt
└── sentiment_data.csv
```

### Important files

| File                            | Purpose                                                                |
| ------------------------------- | ---------------------------------------------------------------------- |
| `manage.py`                     | Django project management entry point                                  |
| `core/views.py`                 | Handles dashboard, text analysis, CSV processing, results, and exports |
| `core/utils.py`                 | Contains the VADER sentiment-analysis logic                            |
| `core/models.py`                | Defines database models                                                |
| `core/urls.py`                  | Defines application routes                                             |
| `templates/dashboard.html`      | Main analysis dashboard                                                |
| `templates/session_detail.html` | Displays session results                                               |
| `requirements.txt`              | Python dependencies                                                    |
| `pyproject.toml`                | Ruff configuration and project tooling                                 |

---

# Sentiment Analysis

SentiMetrics currently uses the VADER sentiment analyzer.

The application extracts the VADER compound score:

```
compound ∈ [-1, +1]
```

The score is then classified using the following logic:

```
if compound_score >= 0.05:
    sentiment = "positive"

elif compound_score <= -0.05:
    sentiment = "negative"

else:
    sentiment = "neutral"
```

### Example

```
Input:
"I absolutely love this product!"

Compound Score:
Positive

Classification:
Positive
```

```
Input:
"This product is okay, nothing special."

Compound Score:
Near zero

Classification:
Neutral
```

```
Input:
"The service was extremely disappointing."

Compound Score:
Negative

Classification:
Negative
```

---

# CSV Batch Processing

SentiMetrics accepts CSV datasets containing a text-based column.

Supported column names include:

```
text
comment
tweet
content
review
message
```

The application automatically detects the first supported column it finds.

### Example

```
review
"The product is amazing."
"The delivery was extremely slow."
"The experience was average."
```

The system processes every valid text entry and associates the results with an analysis session.

For database efficiency, records are inserted using bulk creation in batches.

---

# Using SentiMetrics

## Analyze Individual Text

1. Open the SentiMetrics dashboard.
2. Enter an optional session title.
3. Paste the text you want to analyze.
4. Click **Analyze Text**.
5. View the generated sentiment result.

---

## Analyze a CSV Dataset

1. Prepare a `.csv` file.
2. Make sure it contains a supported text column.
3. Open the SentiMetrics dashboard.
4. Select **Batch CSV Upload**.
5. Choose the CSV file.
6. Enter an optional dataset title.
7. Click **Process Dataset**.
8. Open the generated analysis session.
9. Review the results.
10. Export the session if required.

---

# Output and Reports

Every analyzed text record contains:

```
Text Content
Sentiment Score
Sentiment Label
Analysis Timestamp
```

Reports can be exported as CSV files.

The generated report follows the structure:

```
SentiMetrics_Report_<session_name>.csv
```

---

# Input Validation

SentiMetrics includes several safeguards during CSV processing.

### File validation

```
✓ File exists
✓ File extension is .csv
✓ File size is ≤ 5 MB
✓ File is not empty
✓ CSV contains a header row
✓ CSV contains a supported text column
```

### Text validation

Empty text records are ignored during batch processing.

If no valid text records are found, the analysis session is removed and the user receives an error message.

---

# Example Use Case

Imagine a company has collected 1,000 customer reviews.

Instead of manually reading every review, the team can upload the dataset:

```
customer_reviews.csv
```

SentiMetrics processes the reviews and generates results such as:

```
Review                         Sentiment
------------------------------------------------
"Excellent product!"          Positive
"Delivery was terrible."      Negative
"Product is okay."            Neutral
"Really happy with it."       Positive
"Not worth the price."        Negative
```

The complete result can then be exported for further analysis.

---

# Limitations

SentiMetrics is currently based on VADER sentiment analysis. Therefore, sentiment classification may not always correctly interpret:

* Sarcasm
* Complex context
* Domain-specific terminology
* Ambiguous statements
* Very long or complicated text
* Context that depends on previous sentences
* Mixed or contradictory opinions

For example:

```
"Great, another update that completely broke the application."
```

A rule-based sentiment analyzer may interpret words such as "Great" differently from the intended sarcastic meaning.

---

# Future Improvements

Potential improvements for future versions include:

* Advanced transformer-based sentiment models
* Multi-language sentiment analysis
* Sentiment distribution charts
* Dataset-level analytics
* Sentiment trend visualization
* Keyword and topic extraction
* Aspect-based sentiment analysis
* More detailed analytics dashboards
* Larger dataset support
* Authentication and user accounts
* Cloud deployment
* REST API support
* Real-time sentiment analysis
* PDF report generation
* Automated dataset summaries
* Improved handling of sarcasm and contextual sentiment

---

# Hackathon Focus

SentiMetrics is built around a simple objective:

> **Turn large amounts of unstructured textual feedback into understandable sentiment information.**

The project combines:

```
Web Development
      +
Natural Language Processing
      +
Data Processing
      +
Database Management
      +
Report Generation
```

into a single workflow that allows users to move from **raw text → sentiment → structured results → exportable data**.

---

# Team

SentiMetrics is being developed as a team project for a hackathon.

# License
MIT license

---

## Project Repository

**SentiMetrics**

Built with Python, Django, and VADER Sentiment Analysis.

---

⭐ If you find this project useful, consider giving the repository a star.
