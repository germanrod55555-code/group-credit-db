-- Run once in a NEW, dedicated database. No existing schemas are dropped.
CREATE SCHEMA credit;
CREATE SCHEMA private;
CREATE SCHEMA mart;
CREATE SCHEMA audit;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

CREATE TABLE credit.source_file (
 source_id smallint PRIMARY KEY, filename text NOT NULL UNIQUE,
 url text NOT NULL UNIQUE, sha256 char(64) NOT NULL CHECK(sha256 ~ '^[0-9a-f]{64}$'),
 row_count bigint NOT NULL CHECK(row_count > 0), loaded_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE credit.load_run (
 run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 started_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz,
 status text NOT NULL DEFAULT 'loading' CHECK(status IN ('loading','complete')),
 row_count bigint NOT NULL DEFAULT 0 CHECK(row_count>=0)
);
CREATE TABLE credit.region (code text PRIMARY KEY CHECK(length(code) BETWEEN 1 AND 10));
CREATE TABLE credit.industry (code text PRIMARY KEY, description text NOT NULL);
CREATE TABLE credit.lender (lender_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name text NOT NULL UNIQUE);
CREATE TABLE credit.loan_status (status_code text PRIMARY KEY);
-- Borrowers are fictional teaching cases, not identities inferred from the source.
CREATE TABLE credit.borrower (
 borrower_id bigint PRIMARY KEY, case_code text NOT NULL UNIQUE,
 region_code text NOT NULL REFERENCES credit.region(code),
 industry_code text NOT NULL REFERENCES credit.industry(code),
 synthetic boolean NOT NULL DEFAULT true CHECK(synthetic)
);
CREATE TABLE private.financial_report (
 report_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 borrower_id bigint NOT NULL REFERENCES credit.borrower(borrower_id),
 fiscal_year smallint NOT NULL CHECK(fiscal_year BETWEEN 1980 AND 2100),
 revenue numeric(18,2) NOT NULL CHECK(revenue>0), net_profit numeric(18,2) NOT NULL,
 synthetic boolean NOT NULL DEFAULT true CHECK(synthetic),
 UNIQUE(borrower_id,fiscal_year)
);
CREATE TABLE credit.loan_contract (
 loan_id bigint PRIMARY KEY, borrower_id bigint NOT NULL REFERENCES credit.borrower(borrower_id),
 lender_id bigint NOT NULL REFERENCES credit.lender(lender_id),
 source_id smallint NOT NULL REFERENCES credit.source_file(source_id),
 source_row bigint NOT NULL CHECK(source_row>0),
 approval_date date NOT NULL, amount numeric(18,2) NOT NULL CHECK(amount>=0),
 outstanding numeric(18,2) NOT NULL CHECK(outstanding>=0 AND outstanding<=amount),
 term_months integer CHECK(term_months>=0),
 status_code text NOT NULL REFERENCES credit.loan_status(status_code),
 scenario_fields boolean NOT NULL DEFAULT true CHECK(scenario_fields),
 UNIQUE(source_id,source_row)
);
CREATE TABLE private.collateral (
 collateral_id bigint PRIMARY KEY, kind text NOT NULL CHECK(kind IN ('equipment','property','inventory')),
 appraised_value numeric(18,2) NOT NULL CHECK(appraised_value>=0),
 synthetic boolean NOT NULL DEFAULT true CHECK(synthetic)
);
CREATE TABLE private.loan_collateral (
 loan_id bigint NOT NULL REFERENCES credit.loan_contract(loan_id),
 collateral_id bigint NOT NULL REFERENCES private.collateral(collateral_id),
 allocated_value numeric(18,2) NOT NULL CHECK(allocated_value>=0),
 PRIMARY KEY(loan_id,collateral_id), UNIQUE(collateral_id)
);
CREATE TABLE private.guarantor (
 guarantor_id bigint PRIMARY KEY, display_name text NOT NULL,
 contact_email text NOT NULL UNIQUE CHECK(contact_email LIKE '%@example.invalid'),
 synthetic boolean NOT NULL DEFAULT true CHECK(synthetic)
);
CREATE TABLE private.guarantee (
 loan_id bigint NOT NULL REFERENCES credit.loan_contract(loan_id),
 guarantor_id bigint NOT NULL REFERENCES private.guarantor(guarantor_id),
 amount numeric(18,2) NOT NULL CHECK(amount>0), PRIMARY KEY(loan_id,guarantor_id)
);
CREATE TABLE audit.audit_log (
 audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 event_at timestamptz NOT NULL DEFAULT clock_timestamp(), session_actor text NOT NULL,
 effective_role text NOT NULL, table_name text NOT NULL,
 operation text NOT NULL CHECK(operation IN ('INSERT','UPDATE','DELETE')),
 old_data jsonb, new_data jsonb,
 txid bigint NOT NULL DEFAULT txid_current()
);
-- Additional query indexes are applied separately for the BEFORE/AFTER experiment.
-- PK and UNIQUE indexes remain present in both measurements.
