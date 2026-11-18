-- The reference reporting year is fixed for reproducible comparisons.
CREATE VIEW mart.v_borrower_summary AS
SELECT b.borrower_id,b.case_code,b.region_code,b.industry_code,
 f.fiscal_year,f.revenue,f.net_profit,coalesce(d.debt,0) AS debt,
 CASE WHEN f.revenue IS NULL THEN 'UNKNOWN'
 WHEN coalesce(d.debt,0)/f.revenue>0.5 THEN 'HIGH'
 WHEN coalesce(d.debt,0)/f.revenue>0.25 THEN 'MEDIUM' ELSE 'LOW' END AS risk_level,
 true AS scenario_result
FROM credit.borrower b
LEFT JOIN private.financial_report f ON f.borrower_id=b.borrower_id AND f.fiscal_year=2025
LEFT JOIN (SELECT borrower_id,sum(outstanding) debt FROM credit.loan_contract GROUP BY borrower_id) d ON d.borrower_id=b.borrower_id;

CREATE MATERIALIZED VIEW mart.mv_credit_risk AS SELECT * FROM mart.v_borrower_summary WITH NO DATA;
CREATE UNIQUE INDEX mv_credit_risk_pk ON mart.mv_credit_risk(borrower_id);
-- Refresh is executed after a successful load; the unique index enables later CONCURRENTLY refreshes.
