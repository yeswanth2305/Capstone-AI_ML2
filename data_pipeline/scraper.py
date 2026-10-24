import requests
import pandas as pd

from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://books.toscrape.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


def get_soup(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    response.encoding = response.apparent_encoding

    return BeautifulSoup(
        response.text,
        "html.parser"
    )


def get_category(book_url):
    """Extract category from the book detail page."""

    soup = get_soup(book_url)

    breadcrumb = soup.select("ul.breadcrumb li")

    # Typical structure:
    # Home -> Books -> Category -> Book title

    if len(breadcrumb) >= 3:
        return breadcrumb[2].get_text(strip=True)

    return "Unknown"


def get_rating(book_card):

    rating_tag = book_card.select_one(
        "p.star-rating"
    )

    if not rating_tag:
        return None

    classes = rating_tag.get("class", [])

    for rating_name, rating_value in RATING_MAP.items():

        if rating_name in classes:
            return rating_name

    return None


def scrape_page(page_number):

    url = (
        f"{BASE_URL}"
        f"catalogue/page-{page_number}.html"
    )

    print(f"Scraping: {url}")

    soup = get_soup(url)

    books = []

    for book_card in soup.select(
        "article.product_pod"
    ):

        title_tag = book_card.select_one(
            "h3 a"
        )

        price_tag = book_card.select_one(
            ".price_color"
        )

        availability_tag = book_card.select_one(
            ".availability"
        )

        link = (
            title_tag.get("href")
            if title_tag
            else None
        )

        book_url = (
            urljoin(url, link)
            if link
            else None
        )

        category = (
            get_category(book_url)
            if book_url
            else "Unknown"
        )

        books.append({

            "title": (
                title_tag.get("title", "").strip()
                if title_tag
                else None
            ),

            "price": (
                price_tag.get_text(strip=True)
                if price_tag
                else None
            ),

            "star_rating": get_rating(
                book_card
            ),

            "availability": (
                availability_tag.get_text(
                    " ",
                    strip=True
                )
                if availability_tag
                else None
            ),

            "category": category
        })

    return books


def scrape_books(num_pages=5):

    all_books = []

    for page in range(1, num_pages + 1):

        page_books = scrape_page(page)

        all_books.extend(page_books)

    return pd.DataFrame(all_books)


if __name__ == "__main__":

    df = scrape_books(5)

    print("\n" + "=" * 50)
    print("SCRAPING COMPLETE")
    print("=" * 50)

    print("Number of books:", len(df))

    print("\nCategories:")
    print(df["category"].value_counts())

    print("\nSample:")
    print(df.head())

    df.to_csv(
        "data/books_raw.csv",
        index=False
    )

    print(
        "\nSaved: data/books_raw.csv"
    )