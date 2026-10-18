#!/usr/bin/env python3
"""Check placement and electrical consistency, explicitly allowing unrouted nets."""
import json
import subprocess
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
IMAGE='ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65'
def run(args):
    r=subprocess.run(args,cwd=HERE,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if r.returncode:print(r.stdout);r.check_returncode()
if '--inside' not in sys.argv:
    run(['python3','-B','generate.py'])
    root=HERE.parents[1]
    run(['docker','run','--rm','--platform','linux/amd64','-e','PYTHONDONTWRITEBYTECODE=1',
         '-v',f'{root}:/repo','-w','/repo/hardware/integrated-controller',IMAGE,
         'python3','validate.py','--inside'])
    print((HERE/'output/validation-summary.json').read_text())
    sys.exit()
run(['python3','place-board.py'])
summary=[]
boards=[HERE/'output/knuckles_controller.kicad_pcb',*sorted((HERE/'output/integrated').glob('*/*.kicad_pcb'))]
assert len(boards)==5,'Build both spacings before validation.'
for board in boards:
    prefix=board.stem
    drc=board.with_name(prefix+'-drc.json');erc=board.with_name(prefix+'-erc.json')
    run(['kicad-cli','pcb','drc','--format','json','-o',str(drc),str(board)])
    run(['kicad-cli','sch','erc','--format','json','-o',str(erc),str(board.with_suffix('.kicad_sch'))])
    run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(board.with_suffix('.net.xml')),str(board.with_suffix('.kicad_sch'))])
    d=json.loads(drc.read_text());e=json.loads(erc.read_text())
    ev=[v for sheet in e['sheets'] for v in sheet['violations']]
    row={'board':str(board.relative_to(HERE)),'physical_errors':sum(v['severity']=='error' for v in d['violations']),
         'drc_warnings':sum(v['severity']=='warning' for v in d['violations']),
         'unconnected':len(d['unconnected_items']),'erc_errors':sum(v['severity']=='error' for v in ev),
         'erc_warnings':sum(v['severity']=='warning' for v in ev)}
    summary.append(row)
(HERE/'output/validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
run(['python3','verify.py'])
assert all(r['physical_errors']==r['erc_errors']==0 for r in summary),summary
