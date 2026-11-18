"""COPY -> staging checks -> transactional publication; source-hash idempotency."""
import csv,json,os,hashlib
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import psycopg
ROOT=Path(__file__).resolve().parents[1]
def money(s):return Decimal((s or '0').replace(',','').replace('$',''))
def integer(s):
    if not s.strip():return None
    value=Decimal(s)
    if value!=value.to_integral_value():raise ValueError('Non-integer term in source')
    return int(value)
def read_rows(manifest):
    for source in manifest:
        path=ROOT/'data/raw'/source['filename']
        h=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        if h.hexdigest()!=source['sha256']:raise ValueError('Source checksum mismatch: '+path.name)
        count=0
        with path.open(encoding='utf-8-sig',newline='') as f:
            for n,row in enumerate(csv.DictReader(f),1):
                count=n; sid=source['source_id']; key=sid*10_000_000+n
                date_text=row['ApprovalDate'].split()[0]
                d=datetime.strptime(date_text,'%Y-%m-%d' if '-' in date_text else '%m/%d/%Y').date()
                yield (key,sid,n,row['BorrState'].strip() or 'UNKNOWN',row['NaicsCode'].strip() or 'UNKNOWN',
                    row['NaicsDescription'].strip() or 'Не указана',row['BankName'].strip() or 'UNKNOWN',d,
                    money(row['GrossApproval']),integer(row['TermInMonths']),
                    row['LoanStatus'].strip() or 'UNKNOWN')
        if count!=source['row_count']:raise ValueError('Source row count mismatch')

def load(dsn):
    manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
    with psycopg.connect(dsn) as con:
        # Single-writer lock for this importer. Released automatically at transaction end.
        con.execute('SELECT pg_advisory_xact_lock(182518)')
        prior=con.execute('SELECT source_id,sha256 FROM credit.source_file ORDER BY source_id').fetchall()
        wanted=[(x['source_id'],x['sha256']) for x in manifest]
        if prior:
            if prior==wanted: return {'status':'already_loaded','source_rows':sum(x['row_count'] for x in manifest)}
            raise ValueError('Different snapshot: load into a new database; current source version is immutable')
        run_id=con.execute('INSERT INTO credit.load_run DEFAULT VALUES RETURNING run_id').fetchone()[0]
        con.execute('''CREATE TEMP TABLE stage_loans(
         id bigint PRIMARY KEY,source_id smallint,source_row bigint,region text,industry text,
         industry_description text,lender text,approval_date date,amount numeric(18,2),term_months integer,status text
        ) ON COMMIT DROP''')
        with con.cursor().copy('COPY stage_loans FROM STDIN') as copy:
            for count,row in enumerate(read_rows(manifest),1):
                copy.write_row(row)
                if count%100000==0:print('Staged',count,flush=True)
        total=con.execute('SELECT count(*) FROM stage_loans').fetchone()[0]
        if total<1_000_000:raise ValueError('Need at least one million source records')
        bad=con.execute("SELECT count(*) FROM stage_loans WHERE amount<0 OR approval_date IS NULL OR term_months<0").fetchone()[0]
        if bad:raise ValueError(f'{bad} invalid rows; transaction cancelled')
        for s in manifest:
            con.execute('INSERT INTO credit.source_file(source_id,filename,url,sha256,row_count) VALUES(%s,%s,%s,%s,%s)',
                (s['source_id'],s['filename'],s['url'],s['sha256'],s['row_count']))
        con.execute('INSERT INTO credit.region SELECT DISTINCT region FROM stage_loans')
        con.execute('INSERT INTO credit.industry SELECT industry,min(industry_description) FROM stage_loans GROUP BY industry')
        con.execute('INSERT INTO credit.lender(name) SELECT DISTINCT lender FROM stage_loans')
        con.execute('INSERT INTO credit.loan_status SELECT DISTINCT status FROM stage_loans')
        con.execute("INSERT INTO credit.borrower SELECT id,'CASE-'||id,region,industry,true FROM stage_loans")
        con.execute('''INSERT INTO private.financial_report(borrower_id,fiscal_year,revenue,net_profit)
          SELECT id,extract(year from approval_date)::int-1,greatest(amount*3,1000),round(greatest(amount*3,1000)*0.1,2) FROM stage_loans
          UNION ALL SELECT id,2025,greatest(amount*(1+id%6),1000),round(greatest(amount*(1+id%6),1000)*(id%31-5)/100.0,2) FROM stage_loans''')
        con.execute('''INSERT INTO credit.loan_contract
          SELECT s.id,s.id,l.lender_id,s.source_id,s.source_row,s.approval_date,s.amount,
          CASE WHEN replace(s.status,' ','') IN ('PIF','CANCLD') THEN 0 ELSE round(s.amount*(1+s.id%8)/10.0,2) END,
          s.term_months,s.status,true FROM stage_loans s JOIN credit.lender l ON l.name=s.lender''')
        con.execute("INSERT INTO private.collateral SELECT id,CASE id%3 WHEN 0 THEN 'equipment' WHEN 1 THEN 'property' ELSE 'inventory' END,round(amount*(id%13)/10.0,2),true FROM stage_loans WHERE id%10=0")
        con.execute('INSERT INTO private.loan_collateral SELECT collateral_id,collateral_id,appraised_value FROM private.collateral')
        con.execute("INSERT INTO private.guarantor SELECT id,'Учебный поручитель '||id,'demo-'||id||'@example.invalid',true FROM stage_loans ORDER BY id LIMIT 1000")
        con.execute('INSERT INTO private.guarantee SELECT g.guarantor_id,g.guarantor_id,greatest(l.amount/2,1) FROM private.guarantor g JOIN credit.loan_contract l ON l.loan_id=g.guarantor_id')
        con.execute("UPDATE credit.load_run SET status='complete',finished_at=clock_timestamp(),row_count=%s WHERE run_id=%s",(total,run_id))
        print('Published',total,flush=True)
    return {'status':'loaded','source_rows':total,'run_id':run_id}
if __name__=='__main__':
    result=load(os.environ['DATABASE_URL'])
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/load.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(result)
