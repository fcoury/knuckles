#!/usr/bin/env python3
"""Route only remaining connections; keep the reviewed local cells fixed.

Produces a separate candidate, never overwrites the generated source board.
A candidate passes only with zero physical errors and zero airwires.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import platform
VERSION="2.5.0"
ROUTER="knuckles-freerouting-integrated:"+VERSION
PLATFORM="linux/arm64" if platform.machine() in ["arm64","aarch64"] else "linux/amd64"

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
KICAD='ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65'

def run(args,log=None):
    subprocess.run(args,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT if log else None)

def kicad(*args):
    run(['docker','run','--rm','--platform','linux/amd64','-e','PYTHONDONTWRITEBYTECODE=1',
         '-v',f'{ROOT}:/repo','-w','/repo',KICAD,*map(str,args)])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spacing',choices=['18.5','19.5'],default='18.5')
    p.add_argument('--hand',choices=['left','right'],required=True)
    p.add_argument('--passes',type=int,default=40)
    p.add_argument('--fanout',action='store_true',help='Enable the router SMD fanout pre-pass')
    p.add_argument('--resume',action='store_true',help='Continue routing the existing candidate')
    a=p.parse_args()
    name='knuckles_integrated_'+a.hand
    source=HERE/'output/integrated'/a.spacing/(name+'.kicad_pcb')
    out=HERE/'output/candidates'/a.spacing/a.hand;out.mkdir(parents=True,exist_ok=True)
    def rel(path):return str(path.relative_to(ROOT))
    dsn=out/(name+'.dsn');ses=out/(name+'.ses');board=out/(name+'.kicad_pcb')
    routing_source=board if a.resume else source
    assert routing_source.exists(),routing_source
    for suffix in ['.kicad_pro','.kicad_dru']:
        shutil.copy2(source.with_suffix(suffix),board.with_suffix(suffix))
    (out/'fp-lib-table').write_text('(fp_lib_table (lib (name "Knuckles") (type "KiCad") (uri "${KIPRJMOD}/../../../../libraries/Knuckles.pretty") (options "") (descr "Controller footprints")))\n')
    kicad('python3','kibot/export_dsn.py','-b',rel(routing_source),'-o',rel(dsn))
    text=dsn.read_text()
    # Net classes constrain actual routing even when router UI defaults change.
    text=text.replace('(circuit\n', '(circuit\n        (use_layer F.Cu B.Cu)\n')
    dsn.write_text(text)
    assert '(type fix)' in text,'Critical routes were not exported fixed'
    rules=out/'routing.rules'
    rules.write_text((HERE/'freerouting.rules').read_text().replace('PCB knuckles_integrated','PCB '+name,1))
    run(['docker','build','--platform',PLATFORM,'-t',ROUTER,'docker/freerouting-integrated'])
    with (out/'freerouting.log').open('w') as log:
        run(['docker','run','--rm','--platform',PLATFORM,'-v',f'{ROOT}:/repo',ROUTER,
             '-de','/repo/'+rel(dsn),'-do','/repo/'+rel(ses),'-dr','/repo/'+rel(rules),
             '--router.autorouter.enabled=true',
             '--router.autorouter.max_passes='+str(a.passes),'-mt','1','--router.job_timeout=00:03:00',
             '--router.fanout.enabled='+str(a.fanout).lower(),'--router.optimizer.enabled=false',
             '--router.optimizer.max_threads=1','--gui.enabled=false','--profile.email=knuckles@localhost.invalid'],log)
    kicad('python3','kibot/import_ses.py','-b',rel(routing_source),'-s',rel(ses),'-o',rel(board))
    kicad('python3','hardware/integrated-controller/check-routed.py',rel(source),rel(board))
    report=out/'drc.json'
    kicad('kicad-cli','pcb','drc','--format','json','-o',rel(report),rel(board))
    reference=out/'usb-reference.json'
    try:
        kicad('python3','hardware/integrated-controller/check-reference.py',rel(board),rel(reference))
    except subprocess.CalledProcessError:
        pass # Retain failed measurements in the summary below.
    assembly=out/'assembly.json'
    try:
        kicad('python3','hardware/integrated-controller/check-assembly.py',rel(board),rel(assembly))
    except subprocess.CalledProcessError:
        pass
    d=json.loads(report.read_text())
    result={'board':rel(board),'physical_errors':sum(v['severity']=='error' for v in d['violations']),
            'warnings':sum(v['severity']=='warning' for v in d['violations']),
            'unconnected':len(d['unconnected_items']),'manufacturing_release':False,'router_version':VERSION}
    result['mode']='autoroute-candidate'
    result['source_board_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    result['board_sha256']=hashlib.sha256(board.read_bytes()).hexdigest()
    result['session_sha256']=hashlib.sha256(ses.read_bytes()).hexdigest()
    result['preserved_footprints_and_fixed_routes']=True
    result['reference_pass']=not json.loads(reference.read_text())['unreferenced_samples']
    result['assembly_screen_pass']=not json.loads(assembly.read_text())['via_holes_intersecting_paste_pads']
    result['routing_pass']=result['physical_errors']==result['unconnected']==0 and result['reference_pass'] and result['assembly_screen_pass']
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    if not result['routing_pass']:raise SystemExit(1)

if __name__=='__main__':main()
