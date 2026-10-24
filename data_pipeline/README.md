# Data Pipeline

## Objective

This module implements an end-to-end data pipeline for book catalogue
data from books.toscrape.com.

The pipeline performs:

1. Web scraping
2. Data cleaning
3. Type conversion
4. Fixed-rate currency conversion
5. SQLite normalization
6. SQL querying
7. pandas validation

## Data Source

The source is:

https://books.toscrape.com/

The scraper uses Python's `requests` and `BeautifulSoup` libraries.

Five paginated catalogue pages are scraped automatically.

## Currency Conversion

The project-defined fixed conversion rate is:

1 GBP = 105.50 INR

This is a fixed artificial baseline specified by the assignment.

No external currency API is used.

Therefore:

price_inr = price_gbp * 105.50

## Cleaning Decisions

### Price

The pound symbol (£) is removed and the value is converted to
a floating-point number.

Invalid numeric values are converted to NaN and replaced with
the median GBP price.

### Rating

The textual ratings are mapped as follows:

One   -> 1
Two   -> 2
Three -> 3
Four  -> 4
Five  -> 5

If a rating cannot be parsed, the median rating is used.

### Availability

Rows containing "In stock" are converted to:

True

Other availability values are converted to:

False

### Missing Critical Fields

Rows missing the book title or category are dropped because these
fields are required to identify and classify a book.

## Database Design

The SQLite database contains two normalized tables:

### categories

- category_id: primary key
- category_name: unique category name

### books

- book_id: primary key
- title
- price_gbp
- price_inr
- rating
- in_stock
- category_id: foreign key

The relationship is:

categories (1) -> books (many)

## SQL Queries

The module executes six SQL queries covering:

- SELECT
- WHERE
- ORDER BY
- LIMIT
- DISTINCT
- BETWEEN
- JOIN

The query strings and their outputs are saved in:

outputs/sql_query_outputs.txt

## pandas Validation

At least two SQL query results are loaded using:

pd.read_sql()

The JOIN result is independently reproduced using:

pd.merge()

The two results are compared using:

DataFrame.equals()

The expected result is:

Equivalent: True

## Execution

From the `data_pipeline` directory:

```bash
pip install -r requirements.txt
python scraper.py
python pipeline.py
python queries.py
python pandas_validation.py

---

# 11. One thing I would change for maximum grading safety

The assignment says:

> ≥60 books across ≥3 categories.

Do **not** merely assume five pages will remain sufficient forever. Add an assertion after scraping:

```python
assert len(df) >= 60, (
    f"Expected at least 60 books, got {len(df)}"
)

assert df["category"].nunique() >= 3, (
    "Expected at least 3 categories"
)

# This will cause the script to fail early if the scrape doesn't yield enough data.  
