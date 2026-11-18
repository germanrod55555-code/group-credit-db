CREATE FUNCTION credit.credit_risk(p_borrower_id bigint, p_year integer DEFAULT 2025)
RETURNS text LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = pg_catalog, credit, private AS $$
DECLARE rev numeric; debt numeric;
BEGIN
 SELECT revenue INTO rev FROM private.financial_report
 WHERE borrower_id=p_borrower_id AND fiscal_year=p_year;
 IF rev IS NULL OR rev<=0 THEN RETURN 'UNKNOWN'; END IF;
 SELECT coalesce(sum(outstanding),0) INTO debt FROM credit.loan_contract WHERE borrower_id=p_borrower_id;
 RETURN CASE WHEN debt/rev > 0.5 THEN 'HIGH' WHEN debt/rev > 0.25 THEN 'MEDIUM' ELSE 'LOW' END;
END $$;

CREATE FUNCTION credit.check_loan_limit() RETURNS trigger LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, credit, private AS $$
DECLARE rev numeric;
BEGIN
 SELECT revenue INTO rev FROM private.financial_report
 WHERE borrower_id=NEW.borrower_id AND fiscal_year=extract(year from NEW.approval_date)::int-1
 FOR SHARE;
 IF rev IS NULL THEN RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='Нет отчёта о выручке за год перед одобрением кредита'; END IF;
 IF NEW.amount > rev*0.5 THEN RAISE EXCEPTION USING ERRCODE='23514', MESSAGE='Сумма кредита превышает 50% выручки за предыдущий год'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER loan_limit BEFORE INSERT OR UPDATE ON credit.loan_contract
FOR EACH ROW EXECUTE FUNCTION credit.check_loan_limit();

-- Prevent changing a report from silently invalidating existing contracts.
CREATE FUNCTION credit.check_report_change() RETURNS trigger LANGUAGE plpgsql
SECURITY DEFINER SET search_path = pg_catalog, credit, private AS $$
BEGIN
 IF TG_OP='DELETE' OR NEW.borrower_id<>OLD.borrower_id OR NEW.fiscal_year<>OLD.fiscal_year THEN
   IF EXISTS(SELECT 1 FROM credit.loan_contract WHERE borrower_id=OLD.borrower_id AND extract(year from approval_date)::int=OLD.fiscal_year+1)
   THEN RAISE EXCEPTION 'Нельзя удалить или сменить ключ отчёта, используемого кредитом'; END IF;
 ELSIF EXISTS(SELECT 1 FROM credit.loan_contract WHERE borrower_id=NEW.borrower_id AND extract(year from approval_date)::int=NEW.fiscal_year+1 AND amount>NEW.revenue*0.5)
 THEN RAISE EXCEPTION 'Новая выручка нарушает лимит существующего кредита'; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
CREATE TRIGGER report_limit BEFORE UPDATE OR DELETE ON private.financial_report
FOR EACH ROW EXECUTE FUNCTION credit.check_report_change();

CREATE FUNCTION audit.log_change() RETURNS trigger LANGUAGE plpgsql
SECURITY DEFINER SET search_path=pg_catalog,audit AS $$
BEGIN
 INSERT INTO audit.audit_log(session_actor,effective_role,table_name,operation,old_data,new_data)
 VALUES(session_user,coalesce(nullif(current_setting('role',true),'none'),session_user),
 TG_TABLE_SCHEMA||'.'||TG_TABLE_NAME,TG_OP,
 CASE WHEN TG_OP<>'INSERT' THEN to_jsonb(OLD) END,
 CASE WHEN TG_OP<>'DELETE' THEN to_jsonb(NEW) END);
 RETURN NULL;
END $$;
CREATE TRIGGER report_audit AFTER INSERT OR UPDATE OR DELETE ON private.financial_report FOR EACH ROW EXECUTE FUNCTION audit.log_change();
CREATE TRIGGER guarantor_audit AFTER INSERT OR UPDATE OR DELETE ON private.guarantor FOR EACH ROW EXECUTE FUNCTION audit.log_change();
CREATE TRIGGER collateral_audit AFTER INSERT OR UPDATE OR DELETE ON private.collateral FOR EACH ROW EXECUTE FUNCTION audit.log_change();
CREATE TRIGGER allocation_audit AFTER INSERT OR UPDATE OR DELETE ON private.loan_collateral FOR EACH ROW EXECUTE FUNCTION audit.log_change();
CREATE TRIGGER guarantee_audit AFTER INSERT OR UPDATE OR DELETE ON private.guarantee FOR EACH ROW EXECUTE FUNCTION audit.log_change();
CREATE TRIGGER loan_audit AFTER INSERT OR UPDATE OR DELETE ON credit.loan_contract FOR EACH ROW EXECUTE FUNCTION audit.log_change();
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA credit, audit FROM PUBLIC;
