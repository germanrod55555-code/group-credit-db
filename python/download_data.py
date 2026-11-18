"""Download pinned official SBA snapshots. Raw names/addresses never enter Git."""
import csv, hashlib, json
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
ROOT=Path(__file__).resolve().parents[1]
BASE='https://data.sba.gov/sites/default/files/uploaded_resources/'
FILES=['FOIA_7a_FY2000_FY2009_asof_260930.csv','FOIA_7a_FY2010_FY2019_asof_260930.csv']
def main():
    session=requests.Session()
    session.mount('https://',HTTPAdapter(max_retries=Retry(total=5,backoff_factor=1,status_forcelist=[429,500,502,503,504])))
    raw=ROOT/'data/raw';raw.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for i,name in enumerate(FILES,1):
        p=raw/name
        if not p.exists():
            tmp=p.with_suffix('.part')
            with session.get(BASE+name,stream=True,timeout=(30,120)) as r:
                r.raise_for_status()
                with tmp.open('wb') as f:
                    for chunk in r.iter_content(1024*1024): f.write(chunk)
            tmp.replace(p)
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        with p.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f); rows=sum(1 for _ in reader)
        manifest.append(dict(source_id=i,filename=name,url=BASE+name,sha256=h.hexdigest(),row_count=rows,bytes=p.stat().st_size))
        print(name,rows,'rows',flush=True)
    (ROOT/'data/source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    if sum(x['row_count'] for x in manifest)<1_000_000: raise ValueError('The source dataset must contain at least one million rows')
if __name__=='__main__':main()
