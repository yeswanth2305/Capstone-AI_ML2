# Zepto Data Engineering and Analytics Capstone

This repository contains the capstone implementation covering data collection, data cleaning, relational storage, exploratory analysis, predictive modeling, and model deployment artifacts.

## Project Structure

```text
.
├── data_pipeline/
│   ├── data/
│   │   ├── books_raw.csv
│   │   └── books.db
│   ├── outputs/
│   ├── scraper.py
│   ├── pipeline.py
│   ├── queries.py
│   ├── pandas_validation.py
│   ├── requirements.txt
│   └── README.md
│
├── analytics/
│   ├── data/
│   ├── outputs/
│   ├── models/
│   │   └── titanic_pipeline.joblib
│   ├── 01_eda.ipynb
│   ├── 02_modeling.ipynb
│   ├── titanic.csv
│   ├── requirements.txt
│   └── README.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Module 1 — Data Pipeline

The data pipeline module demonstrates:

```text
Scrape → Clean → Convert → Normalize → Store → Query → Validate
```

Product-style catalogue data is collected from `books.toscrape.com` using `requests` and `BeautifulSoup`.

The pipeline produces at least 60 books across multiple categories, cleans price/rating/availability fields, converts GBP prices to INR, and stores the result in a normalized SQLite database.

The required project-defined currency conversion is:

```text
1 GBP = 105.50 INR
```

This is a fixed artificial project baseline and does not require an external currency API.

The module also demonstrates SQL querying and pandas validation using `pd.read_sql()` and `pd.merge()`.

## Module 2 — Analytics

The analytics module performs Titanic exploratory data analysis and predictive modeling.

The Titanic dataset is loaded once through Seaborn and saved locally as `analytics/titanic.csv` for offline reproducibility.

The module includes:

* Data profiling and missing-value analysis
* Threshold-based cleaning
* Age and fare distribution analysis
* IQR outlier analysis
* Survival analysis
* Correlation analysis
* Multivariate visualizations
* Leakage-safe classification pipelines
* Logistic Regression
* Decision Tree
* Random Forest
* Class imbalance comparison
* SMOTE
* Random Forest GridSearchCV tuning
* Random Forest OOB evaluation
* Multivariate Linear Regression
* Regression diagnostics
* Saved reloadable machine-learning pipeline

## Reproducibility

Each module contains its own requirements file and generated outputs.

The modeling workflow uses preprocessing inside scikit-learn pipelines so that training-only statistics are used during model fitting.

The final classification pipeline is stored at:

```text
analytics/models/titanic_pipeline.joblib
```

## Git Workflow

The repository uses a feature-branch workflow. Development work is performed on a feature branch and merged into `main` after the required commits are completed.
