-- B1_profit
WITH top_profit AS (SELECT borrower_id,net_profit FROM private.financial_report WHERE fiscal_year=2025 ORDER BY net_profit DESC,borrower_id LIMIT 5)
 SELECT b.case_code,t.net_profit,d.debt FROM top_profit t JOIN credit.borrower b USING(borrower_id)
 LEFT JOIN LATERAL (SELECT sum(outstanding) debt FROM credit.loan_contract l WHERE l.borrower_id=t.borrower_id) d ON true;

-- B2_month
SELECT status_code,count(*),sum(amount) FROM credit.loan_contract WHERE approval_date>=DATE '2015-01-01' AND approval_date<DATE '2015-02-01' GROUP BY status_code;

-- B3_lender
SELECT date_trunc('year',approval_date) yr,count(*),sum(amount) FROM credit.loan_contract WHERE lender_id=4 GROUP BY 1;

-- B4_borrower
SELECT borrower_id,sum(outstanding) FROM credit.loan_contract WHERE borrower_id=10000001 GROUP BY borrower_id;

-- B5_region
SELECT industry_code,count(*) FROM credit.borrower WHERE region_code='WY' GROUP BY industry_code;