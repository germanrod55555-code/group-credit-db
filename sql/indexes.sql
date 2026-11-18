CREATE INDEX idx_loan_borrower ON credit.loan_contract(borrower_id) INCLUDE(outstanding);
CREATE INDEX idx_loan_approval ON credit.loan_contract(approval_date) INCLUDE(amount,status_code);
CREATE INDEX idx_loan_lender ON credit.loan_contract(lender_id,approval_date) INCLUDE(amount);
CREATE INDEX idx_financial_year_profit ON private.financial_report(fiscal_year,net_profit DESC) INCLUDE(borrower_id,revenue);
CREATE INDEX idx_borrower_region ON credit.borrower(region_code) INCLUDE(industry_code);
