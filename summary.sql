CREATE TABLE yearly_summary AS
SELECT
    publication_year,
    COUNT(*) AS book_count,
    ROUND(
        AVG(price_cents * CASE WHEN currency = 'EUR' THEN 1.2 ELSE 1 END) / 100.0,
        2
    ) AS average_price
FROM books
GROUP BY publication_year;
