#!/usr/bin/env python3
"""Check placement and electrical consistency, explicitly allowing unrouted nets."""
import hashlib
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
    if '--routed' not in sys.argv:run(['python3','-B','generate.py'])
    root=HERE.parents[1]
    run(['docker','run','--rm','--platform','linux/amd64','-e','PYTHONDONTWRITEBYTECODE=1',
         '-v',f'{root}:/repo','-w','/repo/hardware/integrated-controller',IMAGE,
         'python3','validate.py','--inside',*(['--routed'] if '--routed' in sys.argv else [])])
    print((HERE/('output/routed/validation-summary.json' if '--routed' in sys.argv else 'output/validation-summary.json')).read_text())
    sys.exit()
if '--routed' in sys.argv:
    run(['python3','verify.py'])
    boards=sorted((HERE/'output/routed').glob('*/*/*.kicad_pcb'))
    if len(boards)!=4:raise RuntimeError('Expected four completed keyboard layouts')
    summary=[]
    for board in boards:
        folder=board.parent
        source=HERE/'output/integrated'/folder.parent.name/board.name
        run(['python3','check-routed.py',str(source),str(board)])
        run(['kicad-cli','pcb','drc','--format','json','-o',str(folder/'drc.json'),str(board)])
        run(['python3','check-reference.py',str(board),str(folder/'usb-reference.json')])
        run(['python3','check-assembly.py',str(board),str(folder/'assembly.json')])
        d=json.loads((folder/'drc.json').read_text())
        row={'board':str(board.relative_to(HERE)),
             'physical_errors':sum(v['severity']=='error' for v in d['violations']),
             'warnings':sum(v['severity']=='warning' for v in d['violations']),
             'unconnected':len(d['unconnected_items']),
             'board_sha256':hashlib.sha256(board.read_bytes()).hexdigest(),
             'source_board_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'preserved_footprints_and_fixed_routes':True,
             'reference_pass':True,'assembly_screen_pass':True,
             'mode':'native-kicad-layout','manufacturing_release':False}
        row['routing_pass']=row['physical_errors']==row['unconnected']==0
        (folder/'summary.json').write_text(json.dumps(row,indent=2)+'\n')
        summary.append(row)
    (HERE/'output/routed/validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if not all(r['routing_pass'] for r in summary):raise RuntimeError(summary)
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
    if board.parent.name in {'18.5','19.5'} and row['physical_errors']==0:
        ref=board.with_name(prefix+'-usb-reference.json')
        assembly=board.with_name(prefix+'-assembly.json')
        run(['python3','check-reference.py',str(board),str(ref)])
        run(['python3','check-assembly.py',str(board),str(assembly)])
        row['unreferenced_usb_samples']=len(json.loads(ref.read_text())['unreferenced_samples'])
        row['via_holes_in_paste']=len(json.loads(assembly.read_text())['via_holes_intersecting_paste_pads'])
    summary.append(row)
(HERE/'output/validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
run(['python3','verify.py'])
assert all(r['physical_errors']==r['erc_errors']==0 for r in summary),summary
