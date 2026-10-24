import sqlite3
import pandas as pd


DATABASE = "data/books.db"


QUERIES = {

    "Q1_SELECT_WHERE": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
    """,

    "Q2_ORDER_BY": """
        SELECT title, price_gbp
        FROM books
        ORDER BY price_gbp DESC
    """,

    "Q3_LIMIT": """
        SELECT title, price_inr
        FROM books
        ORDER BY price_inr DESC
        LIMIT 10
    """,

    "Q4_DISTINCT": """
        SELECT DISTINCT category_name
        FROM categories
        ORDER BY category_name
    """,

    "Q5_BETWEEN": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp
    """,

    "Q6_JOIN": """
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
            c.category_name,
            b.rating DESC,
            b.title
    """
}


def main():

    conn = sqlite3.connect(DATABASE)

    with open(
        "outputs/sql_query_outputs.txt",
        "w",
        encoding="utf-8"
    ) as output:

        for name, query in QUERIES.items():

            print("\n" + "=" * 70)
            print(name)
            print("=" * 70)

            print(query)

            df = pd.read_sql(
                query,
                conn
            )

            print(df.to_string(index=False))

            output.write(
                "\n" + "=" * 70 + "\n"
            )

            output.write(
                f"{name}\n"
            )

            output.write(
                "=" * 70 + "\n"
            )

            output.write(
                query.strip() + "\n\n"
            )

            output.write(
                df.to_string(index=False)
            )

            output.write("\n")

    conn.close()


if __name__ == "__main__":
    main()