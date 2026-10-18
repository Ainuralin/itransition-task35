import csv
import json
import re
import sqlite3
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def read_books(path):
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(
        r'"(?:\\.|[^"\\])*"|:([A-Za-z_]\w*)\s*=>',
        lambda match: json.dumps(match[1]) + ":" if match[1] else match[0],
        text,
    )
    return json.loads(text)


def main():
    books = read_books(BASE_DIR / "data" / "task1_d.json")
    rows = []
    for book in books:
        price = book["price"]
        if not re.fullmatch(r"[$€][0-9]+(?:\.[0-9]{1,2})?", price):
            raise ValueError(f"Invalid price: {price!r}")
        currency = "EUR" if price[0] == "€" else "USD"
        price_cents = int(Decimal(price[1:]) * 100)
        rows.append((
            str(book["id"]), book["title"], book["author"],
            book["genre"], book["publisher"], book["year"],
            currency, price_cents,
        ))

    output = BASE_DIR / "output"
    output.mkdir(exist_ok=True)
    with sqlite3.connect(output / "books.db") as connection:
        connection.executescript("""
            DROP TABLE IF EXISTS yearly_summary;
            DROP TABLE IF EXISTS books;
            CREATE TABLE books (
                id TEXT PRIMARY KEY NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                genre TEXT NOT NULL,
                publisher TEXT NOT NULL,
                publication_year INTEGER NOT NULL,
                currency TEXT NOT NULL CHECK (currency IN ('USD', 'EUR')),
                price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
            );
        """)
        connection.executemany(
            "INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows
        )
        connection.executescript(
            (BASE_DIR / "summary.sql").read_text(encoding="utf-8")
        )
        book_count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        summary = connection.execute(
            "SELECT publication_year, book_count, average_price "
            "FROM yearly_summary ORDER BY publication_year"
        ).fetchall()

    header = ("publication_year", "book_count", "average_price")
    with (output / "yearly_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows((year, count, f"{price:.2f}") for year, count, price in summary)

    lines = [
        f"books row count: {book_count}",
        f"yearly_summary row count: {len(summary)}",
        "Exchange rate: EUR 1 = USD 1.2",
        "",
        "| publication_year | book_count | average_price (USD) |",
        "| --- | --- | --- |",
    ]
    lines.extend(f"| {year} | {count} | {price:.2f} |" for year, count, price in summary)
    results = "\n".join(lines) + "\n"
    (output / "summary.txt").write_text(results, encoding="utf-8")
    print(results)
    print(f"Database saved: {output / 'books.db'}")


if __name__ == "__main__":
    main()
