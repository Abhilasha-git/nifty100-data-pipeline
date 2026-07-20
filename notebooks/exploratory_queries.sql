-- 1. Total companies
SELECT COUNT(*) FROM companies;

-- 2. Top 10 ROE
SELECT id, company_name, roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;

-- 3. Top 10 ROCE
SELECT id, company_name, roce_percentage
FROM companies
ORDER BY roce_percentage DESC
LIMIT 10;

-- 4. Top 10 Book Value
SELECT id, company_name, book_value
FROM companies
ORDER BY book_value DESC
LIMIT 10;

-- 5. Latest Net Profit
SELECT c.company_name, p.year, p.net_profit
FROM companies c
JOIN profitandloss p
ON c.id = p.company_id
WHERE p.year = (
    SELECT MAX(year)
    FROM profitandloss p2
    WHERE p2.company_id = p.company_id
)
ORDER BY p.net_profit DESC
LIMIT 10;

-- 6. Latest Sales
SELECT c.company_name, p.year, p.sales
FROM companies c
JOIN profitandloss p
ON c.id = p.company_id
WHERE p.year = (
    SELECT MAX(year)
    FROM profitandloss p2
    WHERE p2.company_id = p.company_id
)
ORDER BY p.sales DESC
LIMIT 10;

-- 7. Dataset Summary
SELECT
(SELECT COUNT(*) FROM companies),
(SELECT COUNT(*) FROM profitandloss),
(SELECT COUNT(*) FROM balancesheet),
(SELECT COUNT(*) FROM cashflow);

-- 8. Random Companies
SELECT *
FROM companies
ORDER BY RANDOM()
LIMIT 5;

-- 9. Year Coverage
SELECT
company_id,
MIN(year),
MAX(year),
COUNT(*)
FROM profitandloss
GROUP BY company_id;

-- 10. Companies with <5 years
SELECT
company_id,
COUNT(*)
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 5;