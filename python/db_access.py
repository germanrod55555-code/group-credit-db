"""Parameterized access, transactional updates, DataFrame export and quality checks."""
import argparse,json,os
from pathlib import Path
from decimal import Decimal
import pandas as pd
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

def borrower(con,borrower_id):
    return con.execute('SELECT * FROM mart.mv_credit_risk WHERE borrower_id=%s',(borrower_id,)).fetchone()

def change_balance(con,loan_id,amount):
    # A transaction/savepoint is rolled back on any exception, including CHECK errors.
    with con.transaction():
        row=con.execute('UPDATE credit.loan_contract SET outstanding=%s WHERE loan_id=%s RETURNING loan_id,outstanding',(amount,loan_id)).fetchone()
        if row is None:raise ValueError('Loan not found')
    return row

def export(con,path):
    # Bounded-memory named cursor; pandas receives one batch at a time.
    total=0
    with con.cursor(name='risk_export',row_factory=dict_row) as cur, Path(path).open('w',encoding='utf-8-sig',newline='') as out:
        cur.execute('SELECT * FROM mart.mv_credit_risk ORDER BY borrower_id')
        while rows:=cur.fetchmany(10000):
            pd.DataFrame(rows).to_csv(out,index=False,header=(total==0));total+=len(rows)
    return total

def quality(con):
    result={}
    for schema,table,key in [('credit','borrower','borrower_id'),('credit','loan_contract','loan_id'),('private','financial_report','report_id')]:
        q=sql.SQL('SELECT count(*) rows,count(*)-count({k}) null_keys,count(*)-count(DISTINCT {k}) duplicate_keys FROM {s}.{t}').format(k=sql.Identifier(key),s=sql.Identifier(schema),t=sql.Identifier(table))
        result[schema+'.'+table]=dict(con.execute(q).fetchone())
    result['missing_reports']=con.execute('''SELECT count(*) n FROM credit.loan_contract l LEFT JOIN private.financial_report f
      ON f.borrower_id=l.borrower_id AND f.fiscal_year=extract(year from l.approval_date)::int-1 WHERE f.report_id IS NULL''').fetchone()['n']
    result['limit_violations']=con.execute('''SELECT count(*) n FROM credit.loan_contract l JOIN private.financial_report f
      ON f.borrower_id=l.borrower_id AND f.fiscal_year=extract(year from l.approval_date)::int-1 WHERE l.amount>f.revenue*0.5''').fetchone()['n']
    result['optional_missing_terms']=con.execute('SELECT count(*) n FROM credit.loan_contract WHERE term_months IS NULL').fetchone()['n']
    return result

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    b=s.add_parser('borrower');b.add_argument('id',type=int)
    u=s.add_parser('balance');u.add_argument('id',type=int);u.add_argument('amount',type=Decimal)
    e=s.add_parser('export');e.add_argument('path',type=Path)
    s.add_parser('quality');a=p.parse_args()
    try:
        with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row) as con:
            if a.command=='borrower':r=borrower(con,a.id)
            elif a.command=='balance':r=change_balance(con,a.id,a.amount)
            elif a.command=='export':r={'exported_rows':export(con,a.path)}
            else:r=quality(con)
        print(json.dumps(r,ensure_ascii=False,indent=2,default=str))
    except (psycopg.Error,ValueError) as exc:
        print('Operation rolled back:',str(exc).splitlines()[0]);raise SystemExit(1)
if __name__=='__main__':main()
