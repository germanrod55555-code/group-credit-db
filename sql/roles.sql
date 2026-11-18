-- Four separate NOLOGIN roles. Assign real LOGIN users outside version control.
CREATE ROLE credit_analyst NOLOGIN;
CREATE ROLE credit_operator NOLOGIN;
CREATE ROLE loan_committee NOLOGIN;
CREATE ROLE credit_admin NOLOGIN;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA credit,private,mart,audit FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA credit,audit FROM PUBLIC;
GRANT USAGE ON SCHEMA mart TO credit_analyst;
GRANT SELECT ON mart.v_borrower_summary,mart.mv_credit_risk TO credit_analyst;
GRANT USAGE ON SCHEMA credit,private,mart TO credit_operator,loan_committee;
GRANT SELECT ON ALL TABLES IN SCHEMA credit,private,mart TO credit_operator,loan_committee;
GRANT INSERT,UPDATE ON credit.loan_contract,private.guarantor,private.guarantee TO credit_operator;
GRANT EXECUTE ON FUNCTION credit.credit_risk(bigint,integer) TO loan_committee,credit_operator;
GRANT USAGE ON SCHEMA credit,private,mart,audit TO credit_admin;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA credit,private TO credit_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA mart,audit TO credit_admin;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA credit,private TO credit_admin;
GRANT EXECUTE ON FUNCTION credit.credit_risk(bigint,integer) TO credit_admin;
-- Admin is an application administrator, not a superuser or owner; audit cannot be altered.
ALTER DEFAULT PRIVILEGES IN SCHEMA credit,private,mart,audit REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA credit,audit REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
