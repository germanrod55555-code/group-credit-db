"""Create the schema, import the pinned snapshot, then enable operational objects."""
import os
from pathlib import Path
import psycopg
from load_data import load
ROOT=Path(__file__).resolve().parents[1]
dsn=os.environ['DATABASE_URL']
with psycopg.connect(dsn) as con:
    if not con.execute("SELECT to_regnamespace('credit')").fetchone()[0]:
        con.execute((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))
    elif con.execute("SELECT to_regprocedure('credit.credit_risk(bigint,integer)')").fetchone()[0]:
        raise SystemExit('Database is already configured. Use load_data.py for the idempotency check.')
load(dsn)
with psycopg.connect(dsn) as con:
    for name in ['triggers_functions.sql','views.sql','roles.sql']:
        con.execute((ROOT/'sql'/name).read_text(encoding='utf-8'))
    con.execute('REFRESH MATERIALIZED VIEW mart.mv_credit_risk')
with psycopg.connect(dsn,autocommit=True) as con:
    con.execute('VACUUM (ANALYZE)')
print('Setup complete. Run benchmark.py to create and measure additional indexes.')
