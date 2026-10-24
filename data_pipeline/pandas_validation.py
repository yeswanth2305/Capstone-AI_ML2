import sqlite3
import pandas as pd


DATABASE = "data/books.db"


def main():

    conn = sqlite3.connect(DATABASE)

    # --------------------------------------------------
    # SQL RESULT 1
    # --------------------------------------------------

    high_rated_sql = """
        SELECT
            title,
            rating,
            price_gbp
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC
    """

    high_rated_df = pd.read_sql(
        high_rated_sql,
        conn
    )

    # --------------------------------------------------
    # SQL RESULT 2
    # --------------------------------------------------

    expensive_sql = """
        SELECT
            title,
            price_gbp,
            price_inr
        FROM books
        WHERE price_gbp BETWEEN 30 AND 50
        ORDER BY price_gbp DESC
    """

    expensive_df = pd.read_sql(
        expensive_sql,
        conn
    )

    # --------------------------------------------------
    # JOIN USING SQL
    # --------------------------------------------------

    join_sql = """
        SELECT
            b.title,
            c.category_name,
            b.rating,
            b.price_gbp,
            b.price_inr,
            b.in_stock
        FROM books b
        JOIN categories c
            ON b.category_id = c.category_id
        ORDER BY
            b.title
    """

    sql_join_df = pd.read_sql(
        join_sql,
        conn
    )

    # --------------------------------------------------
    # READ TABLES DIRECTLY
    # --------------------------------------------------

    books_df = pd.read_sql(
        """
        SELECT *
        FROM books
        """,
        conn
    )

    categories_df = pd.read_sql(
        """
        SELECT *
        FROM categories
        """,
        conn
    )

    # --------------------------------------------------
    # REPRODUCE JOIN USING pd.merge
    # --------------------------------------------------

    merged_df = pd.merge(
        books_df,
        categories_df,
        on="category_id",
        how="inner"
    )

    merged_df = merged_df[
        [
            "title",
            "category_name",
            "rating",
            "price_gbp",
            "price_inr",
            "in_stock"
        ]
    ]

    merged_df = merged_df.sort_values(
        "title"
    ).reset_index(drop=True)

    sql_join_df = sql_join_df.sort_values(
        "title"
    ).reset_index(drop=True)

    # --------------------------------------------------
    # COMPARISON
    # --------------------------------------------------

    equivalent = sql_join_df.equals(
        merged_df
    )

    print("\n" + "=" * 60)
    print("pd.read_sql RESULT")
    print("=" * 60)

    print(sql_join_df.to_string(index=False))

    print("\n" + "=" * 60)
    print("pd.merge RESULT")
    print("=" * 60)

    print(merged_df.to_string(index=False))

    print("\nEquivalent:", equivalent)

    # Save outputs

    with open(
        "outputs/pandas_results.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "QUERY RESULT 1 - HIGH RATED BOOKS\n"
        )

        f.write(
            high_rated_df.to_string(
                index=False
            )
        )

        f.write(
            "\n\nQUERY RESULT 2 - PRICE RANGE\n"
        )

        f.write(
            expensive_df.to_string(
                index=False
            )
        )

        f.write(
            "\n\nSQL JOIN RESULT\n"
        )

        f.write(
            sql_join_df.to_string(
                index=False
            )
        )

        f.write(
            "\n\nPANDAS MERGE RESULT\n"
        )

        f.write(
            merged_df.to_string(
                index=False
            )
        )

        f.write(
            f"\n\nEquivalent: {equivalent}\n"
        )

    conn.close()


if __name__ == "__main__":
    main()