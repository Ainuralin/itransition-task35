# Task 3.5

Load book data into SQLite and calculate the number of books and average price
in USD for each publication year.

## Run

Python 3.9 or newer. No additional packages are needed.

```bash
python load_books.py
```

The script creates `output/books.db` with two tables: `books` and
`yearly_summary`. It also exports `output/yearly_summary.csv` and
`output/summary.txt`. Running it again rebuilds both tables.

`summary.sql` contains the aggregation query. `verify.sql` contains queries
to inspect the tables and check row counts in a SQLite viewer.

## Notes

- The supplied `.json` file uses Ruby-style keys (`:id=>`). These are converted
  before parsing; quoted strings are preserved.
- IDs are stored as text because their values exceed SQLite's integer range.
- Prices are stored in cents with their original currency. EUR prices are
  converted at EUR 1 = USD 1.2; only the final yearly average is rounded.

The input contains 5,003 books. The summary contains 49 publication years.
