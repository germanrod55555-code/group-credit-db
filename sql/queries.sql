-- Q1 = B1. CTE + JOIN: TOP-5 by scenario profit for 2025 and total unpaid debt.
WITH top_profit AS (
 SELECT borrower_id,net_profit FROM private.financial_report
 WHERE fiscal_year=2025 ORDER BY net_profit DESC,borrower_id LIMIT 5
)
SELECT b.case_code,t.net_profit,d.debt FROM top_profit t JOIN credit.borrower b USING(borrower_id)
LEFT JOIN LATERAL (SELECT sum(outstanding) debt FROM credit.loan_contract l WHERE l.borrower_id=t.borrower_id) d ON true;

-- Q2. Contracts with total allocated collateral strictly below 80% (including no collateral).
SELECT l.loan_id,l.amount,coalesce(c.coverage,0) coverage FROM credit.loan_contract l
LEFT JOIN (SELECT loan_id,sum(allocated_value) coverage FROM private.loan_collateral GROUP BY loan_id) c USING(loan_id)
WHERE coalesce(c.coverage,0)<0.8*l.amount ORDER BY l.loan_id;

-- Q3 = B2. Monthly original approval volume by status (January 2015).
SELECT status_code,count(*),sum(amount) FROM credit.loan_contract
WHERE approval_date>=DATE '2015-01-01' AND approval_date<DATE '2015-02-01' GROUP BY status_code;

-- Q4 = B3. Annual approval volume for a selected lender; benchmark saves its actual ID.
SELECT date_trunc('year',approval_date) yr,count(*),sum(amount) FROM credit.loan_contract
WHERE lender_id=(SELECT lender_id FROM credit.loan_contract GROUP BY lender_id HAVING count(*) BETWEEN 100 AND 200 ORDER BY lender_id LIMIT 1)
GROUP BY 1;

-- Q5 = B4. Total outstanding debt for one teaching borrower.
SELECT borrower_id,sum(outstanding) FROM credit.loan_contract WHERE borrower_id=10000001 GROUP BY borrower_id;

-- Q6 = B5. Industry breakdown in a selected region.
SELECT industry_code,count(*) FROM credit.borrower WHERE region_code='WY' GROUP BY industry_code;

-- Q7. JOIN + GROUP BY: original approval amounts by industry.
SELECT i.code,i.description,count(*) contracts,sum(l.amount) approved
FROM credit.loan_contract l JOIN credit.borrower b USING(borrower_id)
JOIN credit.industry i ON i.code=b.industry_code GROUP BY i.code,i.description ORDER BY approved DESC;

-- Q8. Ranking lenders within each calendar year, using a window function.
WITH totals AS (SELECT extract(year from approval_date)::int yr,lender_id,sum(amount) total
 FROM credit.loan_contract GROUP BY 1,2)
SELECT yr,lender_id,total,dense_rank() OVER(PARTITION BY yr ORDER BY total DESC) rank_in_year FROM totals;

-- Additional mart usage: SELECT risk_level,count(*) FROM mart.mv_credit_risk GROUP BY risk_level;
-- REFRESH MATERIALIZED VIEW mart.mv_credit_risk;
-- Subsequent refresh, as owner and outside a transaction: REFRESH MATERIALIZED VIEW CONCURRENTLY mart.mv_credit_risk;
