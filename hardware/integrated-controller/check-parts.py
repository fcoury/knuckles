#!/usr/bin/env python3
"""Snapshot public JLCPCB catalog data; this does not reserve or buy parts."""
import concurrent.futures
import datetime
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
from circuit import PARTS
CODES = sorted({p['lcsc'] for p in PARTS if p['lcsc']})

def fetch(code):
    url = 'https://jlcpcb.com/partdetail/' + code
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read().decode()
        chunks=[]
        for m in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>',html):
            try:
                value=json.loads(m[1])
                if isinstance(value[1],str):chunks.append(value[1])
            except (ValueError,IndexError):pass
        records=[]
        for m in re.finditer(r'(?m)^[0-9a-f]+:(\{.*)', ''.join(chunks)):
            try:record=json.loads(m[1])
            except ValueError:continue
            if isinstance(record,dict) and record.get('componentCode')==code:records.append(record)
        merged={k:v for record in records for k,v in record.items() if v is not None and not (isinstance(v,str) and v.startswith('$'))}
        wanted=['componentCode','componentModelEn','componentBrandEn','componentSpecificationEn','assemblyMode','componentLibraryType','overseasStockCount','canPresaleNumber','preMinPurchaseNum','leastPatchNumber','lossNumber','noBuyReason','dataManualUrl','initialPrice']
        result={k:merged[k] for k in wanted if k in merged}
        result.update(url=url,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        if not result.get('componentModelEn'):result.update(componentCode=code, error='Catalog page did not expose matching structured part data')
        return result
    except Exception as e:return {'componentCode':code,'url':url,'error':str(e)}

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        records=list(executor.map(fetch,CODES))
    (ROOT/'parts-snapshot.json').write_text(json.dumps(records,indent=2)+'\n')
    for r in records:print(r.get('componentCode'),r.get('componentModelEn'),r.get('componentSpecificationEn'),r.get('overseasStockCount'),r.get('error',''))
