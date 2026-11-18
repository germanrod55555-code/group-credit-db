-- Q1. Top five borrowers by scenario profit for the last complete reporting year.
WITH top_profit AS (
 SELECT borrower_id,net_profit FROM private.financial_report
 WHERE fiscal_year=2025 ORDER BY net_profit DESC,borrower_id LIMIT 5
), debts AS (SELECT borrower_id,sum(outstanding) debt FROM credit.loan_contract GROUP BY borrower_id)
SELECT b.case_code,t.net_profit,coalesce(d.debt,0) debt FROM top_profit t
JOIN credit.borrower b USING(borrower_id) LEFT JOIN debts d USING(borrower_id)
ORDER BY t.net_profit DESC,b.borrower_id;

-- Q2. Contracts with total allocated collateral strictly below 80% (including no collateral).
SELECT l.loan_id,l.amount,coalesce(c.coverage,0) coverage FROM credit.loan_contract l
LEFT JOIN (SELECT loan_id,sum(allocated_value) coverage FROM private.loan_collateral GROUP BY loan_id) c USING(loan_id)
WHERE coalesce(c.coverage,0)<0.8*l.amount ORDER BY l.loan_id;

-- Q3. JOIN + GROUP BY: original approval amounts by industry.
SELECT i.code,i.description,count(*) contracts,sum(l.amount) approved
FROM credit.loan_contract l JOIN credit.borrower b USING(borrower_id)
JOIN credit.industry i ON i.code=b.industry_code GROUP BY i.code,i.description ORDER BY approved DESC;

-- Q4. Ranking lenders within each calendar year, using a window function.
WITH totals AS (SELECT extract(year from approval_date)::int yr,lender_id,sum(amount) total
 FROM credit.loan_contract GROUP BY 1,2)
SELECT yr,lender_id,total,dense_rank() OVER(PARTITION BY yr ORDER BY total DESC) rank_in_year FROM totals;

-- Q5. Risk distribution. All risk figures are scenario results, not SBA credit ratings.
SELECT risk_level,count(*) borrowers,sum(debt) debt FROM mart.mv_credit_risk GROUP BY risk_level;

-- Q6. Contract volume and amount by region.
SELECT b.region_code,count(*) contracts,sum(l.amount) approved FROM credit.borrower b
JOIN credit.loan_contract l USING(borrower_id) GROUP BY b.region_code ORDER BY approved DESC;

-- Q7. Missing collateral coverage, TOP 20 largest shortfalls.
SELECT l.loan_id,l.amount-coalesce(c.coverage,0) shortfall FROM credit.loan_contract l
LEFT JOIN (SELECT loan_id,sum(allocated_value) coverage FROM private.loan_collateral GROUP BY loan_id) c USING(loan_id)
ORDER BY shortfall DESC,l.loan_id LIMIT 20;

-- Q8. Latest scenario financial statement per borrower.
SELECT borrower_id,fiscal_year,revenue,net_profit FROM (
 SELECT *,row_number() OVER(PARTITION BY borrower_id ORDER BY fiscal_year DESC) rn FROM private.financial_report
) ranked WHERE rn=1;
-- REFRESH MATERIALIZED VIEW mart.mv_credit_risk;
-- Subsequent refresh, as owner and outside a transaction: REFRESH MATERIALIZED VIEW CONCURRENTLY mart.mv_credit_risk;
