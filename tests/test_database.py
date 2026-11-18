"""Integration tests against a dedicated installed teaching database; changes roll back."""
import os,sys,unittest,json
from pathlib import Path
from decimal import Decimal
import psycopg
from psycopg.rows import dict_row
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
from db_access import change_balance,borrower

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.c=psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row)
        self.loan=self.c.execute('SELECT * FROM credit.loan_contract WHERE amount>1000 ORDER BY loan_id LIMIT 1').fetchone()
        self.id=self.loan['loan_id'];self.year=self.loan['approval_date'].year-1
    def tearDown(self):self.c.rollback();self.c.close()
    def denied(self,role,query,params=None):
        with self.assertRaises(psycopg.errors.InsufficientPrivilege):
            with self.c.transaction():
                self.c.execute('SET LOCAL ROLE '+role);self.c.execute(query,params)
    def test_source_million(self):
        self.assertGreaterEqual(self.c.execute('SELECT sum(row_count) n FROM credit.source_file').fetchone()['n'],1_000_000)
        # SBA exports the paid-in-full status as "P I F", including spaces.
        self.assertGreater(self.c.execute("SELECT count(*) n FROM credit.loan_contract WHERE status_code='P I F'").fetchone()['n'],0)
        self.assertEqual(self.c.execute("SELECT count(*) n FROM credit.loan_contract WHERE replace(status_code,' ','') IN ('PIF','CANCLD') AND outstanding<>0").fetchone()['n'],0)
    def test_minimum_tables(self):
        self.assertGreaterEqual(self.c.execute("SELECT count(*) n FROM information_schema.tables WHERE table_schema IN ('credit','private','audit') AND table_type='BASE TABLE'").fetchone()['n'],8)
    def test_parameterized_lookup(self):self.assertEqual(borrower(self.c,self.id)['borrower_id'],self.id)
    def test_missing_lookup(self):self.assertIsNone(borrower(self.c,-1))
    def test_balance_transaction(self):
        self.assertEqual(change_balance(self.c,self.id,Decimal('10'))['outstanding'],Decimal('10'))
    def test_balance_rollback(self):
        old=self.loan['outstanding']
        with self.assertRaises(psycopg.errors.CheckViolation):change_balance(self.c,self.id,Decimal('-1'))
        self.assertEqual(self.c.execute('SELECT outstanding FROM credit.loan_contract WHERE loan_id=%s',(self.id,)).fetchone()['outstanding'],old)
    def test_loan_limit_rejects(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            with self.c.transaction():self.c.execute('UPDATE credit.loan_contract SET amount=amount*2 WHERE loan_id=%s',(self.id,))
    def test_loan_limit_accepts_boundary(self):
        self.c.execute('UPDATE credit.loan_contract SET amount=amount*1.5 WHERE loan_id=%s',(self.id,))
    def test_missing_previous_report(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            with self.c.transaction():self.c.execute("UPDATE credit.loan_contract SET approval_date=DATE '1985-01-01' WHERE loan_id=%s",(self.id,))
    def test_report_reduction_rejected(self):
        with self.assertRaises(psycopg.Error):
            with self.c.transaction():self.c.execute('UPDATE private.financial_report SET revenue=1 WHERE borrower_id=%s AND fiscal_year=%s',(self.id,self.year))
    def test_audit_contains_before_after_actor(self):
        self.c.execute('SET LOCAL ROLE credit_operator')
        change_balance(self.c,self.id,Decimal('11'))
        self.c.execute('RESET ROLE')
        row=self.c.execute("SELECT * FROM audit.audit_log WHERE table_name='credit.loan_contract' AND new_data->>'loan_id'=%s ORDER BY audit_id DESC LIMIT 1",(str(self.id),)).fetchone()
        self.assertEqual(row['operation'],'UPDATE');self.assertEqual(row['effective_role'],'credit_operator')
        self.assertEqual(Decimal(str(row['new_data']['outstanding'])),Decimal('11'));self.assertIsNotNone(row['old_data'])
    def test_analyst_mart_read(self):
        self.c.execute('SET LOCAL ROLE credit_analyst');self.assertIsNotNone(borrower(self.c,self.id))
    def test_analyst_private_denied(self):self.denied('credit_analyst','SELECT * FROM private.guarantor LIMIT 1')
    def test_analyst_source_denied(self):self.denied('credit_analyst','SELECT * FROM credit.loan_contract LIMIT 1')
    def test_operator_delete_denied(self):self.denied('credit_operator','DELETE FROM credit.loan_contract WHERE loan_id=-1')
    def test_committee_update_denied(self):self.denied('loan_committee','UPDATE credit.loan_contract SET outstanding=0 WHERE loan_id=-1')
    def test_admin_audit_update_denied(self):self.denied('credit_admin','DELETE FROM audit.audit_log WHERE audit_id=-1')
    def test_function_unknown(self):
        self.assertEqual(self.c.execute('SELECT credit.credit_risk(-1,2025) risk').fetchone()['risk'],'UNKNOWN')
    def test_function_thresholds(self):
        self.c.execute('UPDATE credit.loan_contract SET outstanding=amount WHERE loan_id=%s',(self.id,))
        for factor,expected in [(1,'HIGH'),(2,'MEDIUM'),(4,'LOW')]:
            self.c.execute('UPDATE private.financial_report SET revenue=%s WHERE borrower_id=%s AND fiscal_year=2025',(self.loan['amount']*factor,self.id))
            self.assertEqual(self.c.execute('SELECT credit.credit_risk(%s,2025) risk',(self.id,)).fetchone()['risk'],expected)
    def test_snapshot_has_no_contacts(self):
        cols=[x['column_name'] for x in self.c.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='mart' AND table_name='v_borrower_summary'").fetchall()]
        self.assertNotIn('contact_email',cols);self.assertNotIn('display_name',cols)
    def test_fk(self):
        with self.assertRaises(psycopg.errors.ForeignKeyViolation):
            with self.c.transaction():self.c.execute('INSERT INTO private.guarantee VALUES(-1,10000001,1)')
    def test_unique(self):
        with self.assertRaises(psycopg.errors.UniqueViolation):
            with self.c.transaction():self.c.execute('INSERT INTO credit.region SELECT * FROM credit.region LIMIT 1')
    def test_check_contact_domain(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            with self.c.transaction():self.c.execute("INSERT INTO private.guarantor VALUES(-100,'Test','real@domain.com',true)")

if __name__=='__main__':unittest.main(verbosity=2)
