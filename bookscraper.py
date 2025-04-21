import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from currency_converter import CurrencyConverter
import re

numbers_conversion = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
session = requests.Session()
converter = CurrencyConverter()

def fetch_book_details(book_url, title, rating_text):
    try:
        response = session.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        breadcrumb = soup.find("ul", class_="breadcrumb")
        category = breadcrumb.find_all("a")[2].text.strip()

        stock_text = soup.find("p", class_="instock availability").text.strip().lower()
        stock = int(re.search(r'\d+', stock_text).group()) if "in stock" in stock_text else 0

        price_text = soup.find("p", class_="price_color").text.strip()
        price = round(converter.convert(float(price_text[1:]), "GBP", "EUR"), 1)

        rating = numbers_conversion.get(rating_text, 0)
        description = soup.find("meta", attrs={"name": "description"})["content"].replace('"', "'")
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()


        return [title, rating, price, stock, category, description]

    except Exception as e:
        print(f"Error fetching book: {title} — {type(e).__name__}: {e}")
        return None

def scraper(page):
    base_url = "https://books.toscrape.com/catalogue/"
    page_url = f"{base_url}page-{page}.html"
    result = []

    try:
        response = session.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        book_list = soup.find("ol", class_="row")

        book_entries = []

        for book in book_list.find_all("article", class_="product_pod"):
            title = book.h3.a["title"]
            relative_url = book.h3.a["href"]
            full_url = f"{base_url}{relative_url}"
            rating_text = book.p["class"][1]

            book_entries.append((full_url, title, rating_text))

        with ThreadPoolExecutor(max_workers=10) as book_executor:
            book_data = book_executor.map(lambda args: fetch_book_details(*args), book_entries)

        result.extend([b for b in book_data if b is not None])

        return result

    except Exception as e:
        print(f"Error on page {page}: {type(e).__name__}: {e}")
        return []


with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(scraper, range(1, 51))

all_books = [book for page in results for book in page]

bookshelf = pd.DataFrame(all_books, columns=["Title", "Rating", "Price", "Stock", "Category", "Description"])

print(f"Total books scraped: {len(bookshelf)}")
bookshelf.to_csv("./csv/bookshelf.csv", index=False)