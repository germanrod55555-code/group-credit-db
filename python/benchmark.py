"""Five BEFORE/AFTER plans; fixed warm-cache methodology, no fabricated cold cache."""
import json,os,statistics,platform
from pathlib import Path
import psycopg
ROOT=Path(__file__).resolve().parents[1]
QUERIES={
 'B1_profit':'''WITH top_profit AS (SELECT borrower_id,net_profit FROM private.financial_report WHERE fiscal_year=2025 ORDER BY net_profit DESC,borrower_id LIMIT 5)
 SELECT b.case_code,t.net_profit,d.debt FROM top_profit t JOIN credit.borrower b USING(borrower_id)
 LEFT JOIN LATERAL (SELECT sum(outstanding) debt FROM credit.loan_contract l WHERE l.borrower_id=t.borrower_id) d ON true''',
 'B2_month':"SELECT status_code,count(*),sum(amount) FROM credit.loan_contract WHERE approval_date>=DATE '2015-01-01' AND approval_date<DATE '2015-02-01' GROUP BY status_code",
 'B3_lender':"SELECT date_trunc('year',approval_date) yr,count(*),sum(amount) FROM credit.loan_contract WHERE lender_id=(SELECT lender_id FROM credit.lender WHERE name='UNKNOWN') GROUP BY 1",
 'B4_borrower':"SELECT borrower_id,sum(outstanding) FROM credit.loan_contract WHERE borrower_id=10000001 GROUP BY borrower_id",
 'B5_region':"SELECT industry_code,count(*) FROM credit.borrower WHERE region_code='WY' GROUP BY industry_code"
}
INDEXES=['idx_loan_borrower','idx_loan_approval','idx_loan_lender','idx_financial_year_profit','idx_borrower_region']
def scans(node):
    out=[]
    if 'Scan' in node['Node Type']:out.append(node['Node Type']+(' '+node['Index Name'] if 'Index Name' in node else ''))
    for p in node.get('Plans',[]):out+=scans(p)
    return sorted(set(out))
def main():
    folder=ROOT/'results/explain';folder.mkdir(parents=True,exist_ok=True)
    summary={}
    with psycopg.connect(os.environ['DATABASE_URL'],autocommit=True,prepare_threshold=None) as con:
        # Never force a planner to use indexes. Both phases use the same configuration.
        con.execute('SET jit=off');con.execute('SET max_parallel_workers_per_gather=0')
        con.execute('SET statement_timeout=120000')
        # Select a real, uncommon lender instead of a guessed name/id.
        lender=con.execute('SELECT lender_id FROM credit.loan_contract GROUP BY lender_id HAVING count(*) BETWEEN 100 AND 200 ORDER BY lender_id LIMIT 1').fetchone()[0]
        QUERIES['B3_lender']=f"SELECT date_trunc('year',approval_date) yr,count(*),sum(amount) FROM credit.loan_contract WHERE lender_id={lender} GROUP BY 1"
        for name in INDEXES:con.execute('DROP INDEX IF EXISTS '+('private.' if name.startswith('idx_financial') else 'credit.')+name)
        for phase in ['before','after']:
            if phase=='after':con.execute((ROOT/'sql/indexes.sql').read_text(encoding='utf-8'))
            con.execute('VACUUM (ANALYZE)')
            for key,q in QUERIES.items():
                runs=[]
                for run in range(4):
                    plan=con.execute('EXPLAIN (ANALYZE,BUFFERS,SETTINGS,FORMAT JSON) '+q).fetchone()[0][0]
                    (folder/f'{key}_{phase}_{run}.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
                    if run:runs.append(plan)
                chosen=sorted(runs,key=lambda p:p['Execution Time'])[1]
                summary.setdefault(key,{'sql':q})[phase]={
                 'median_ms':statistics.median(p['Execution Time'] for p in runs),
                 'planning_ms':chosen['Planning Time'],'shared_hit':chosen['Plan'].get('Shared Hit Blocks',0),
                 'shared_read':chosen['Plan'].get('Shared Read Blocks',0),'temp_read':chosen['Plan'].get('Temp Read Blocks',0),
                 'temp_written':chosen['Plan'].get('Temp Written Blocks',0),'rows':chosen['Plan']['Actual Rows'],
                 'scans':scans(chosen['Plan'])}
                print(phase,key,summary[key][phase]['median_ms'],flush=True)
        env={'server':con.execute('SELECT version()').fetchone()[0], 'platform':platform.platform(),
             'source_rows':con.execute('SELECT count(*) FROM credit.loan_contract').fetchone()[0],
             'shared_buffers':con.execute('SHOW shared_buffers').fetchone()[0],
             'method':'one warmup + three measured runs; warm/steady cache, not cold; JIT off, parallel 0; same data and PK/UNIQUE indexes'}
    (ROOT/'results/benchmark.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (ROOT/'results/environment.json').write_text(json.dumps(env,indent=2),encoding='utf-8')
    (ROOT/'sql/benchmark_queries.sql').write_text('\n\n'.join('-- '+k+'\n'+q+';' for k,q in QUERIES.items()),encoding='utf-8')
if __name__=='__main__':main()
