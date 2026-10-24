import sqlite3
import pandas as pd
import numpy as np


RAW_FILE = "data/books_raw.csv"
DATABASE = "data/books.db"

GBP_TO_INR = 105.50


def clean_data(df):

    df = df.copy()

    # ==================================================
    # PRICE
    # ==================================================

    df["price_gbp"] = (
        df["price"]
        .astype("string")
        .str.replace("Â£", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["price_gbp"] = pd.to_numeric(
        df["price_gbp"],
        errors="coerce"
    )

    invalid_prices = df["price_gbp"].isna().sum()

    print(
        "Invalid price values:",
        invalid_prices
    )

    if invalid_prices > 0:

        median_price = df["price_gbp"].median()

        if pd.isna(median_price):
            raise ValueError(
                "All price values failed to parse. "
                "Check the raw price column."
            )

        df["price_gbp"] = (
            df["price_gbp"]
            .fillna(median_price)
        )

    # --------------------------------------------------
    # RATING
    # --------------------------------------------------

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    df["rating"] = (
        df["star_rating"]
        .map(rating_map)
    )

    # Median imputation for numeric rating
    if df["rating"].isna().any():

        median_rating = int(
            round(df["rating"].median())
        )

        df["rating"] = (
            df["rating"]
            .fillna(median_rating)
        )

    # --------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------

    df["in_stock"] = (
        df["availability"]
        .astype(str)
        .str.contains(
            "In stock",
            case=False,
            na=False
        )
    )

    # --------------------------------------------------
    # PRICE IMPUTATION
    # --------------------------------------------------

    if df["price_gbp"].isna().any():

        median_price = df[
            "price_gbp"
        ].median()

        df["price_gbp"] = (
            df["price_gbp"]
            .fillna(median_price)
        )

    # --------------------------------------------------
    # FIXED CURRENCY CONVERSION
    # --------------------------------------------------

    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    # --------------------------------------------------
    # DROP ROWS WITH CRITICAL MISSING TEXT
    # --------------------------------------------------

    df = df.dropna(
        subset=[
            "title",
            "category"
        ]
    )

    return df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category"
        ]
    ]


def create_database(df):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute(
        "PRAGMA foreign_keys = ON"
    )

    # --------------------------------------------------
    # CATEGORIES TABLE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL UNIQUE
        )
    """)

    # --------------------------------------------------
    # BOOKS TABLE
    # --------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL,
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,

            FOREIGN KEY (category_id)
                REFERENCES categories(category_id)
        )
    """)

    # Clear previous data for reproducibility
    cursor.execute("DELETE FROM books")
    cursor.execute("DELETE FROM categories")

    # --------------------------------------------------
    # INSERT CATEGORIES
    # --------------------------------------------------

    categories = (
        df["category"]
        .drop_duplicates()
        .tolist()
    )

    cursor.executemany(
        """
        INSERT INTO categories(category_name)
        VALUES (?)
        """,
        [(category,) for category in categories]
    )

    # --------------------------------------------------
    # INSERT BOOKS
    # --------------------------------------------------

    for _, row in df.iterrows():

        cursor.execute(
            """
            SELECT category_id
            FROM categories
            WHERE category_name = ?
            """,
            (row["category"],)
        )

        category_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO books
            (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                row["title"],
                float(row["price_gbp"]),
                float(row["price_inr"]),
                int(row["rating"]),
                int(row["in_stock"]),
                category_id
            )
        )

    conn.commit()

    return conn


if __name__ == "__main__":

    print("Loading raw data...")

    raw_df = pd.read_csv(RAW_FILE)

    print(
        "Raw rows:",
        len(raw_df)
    )

    cleaned_df = clean_data(raw_df)

    print(
        "Cleaned rows:",
        len(cleaned_df)
    )

    print("\nData types:")
    print(cleaned_df.dtypes)

    print("\nSample:")
    print(cleaned_df.head())

    conn = create_database(cleaned_df)

    print(
        f"\nDatabase created: {DATABASE}"
    )

    conn.close()