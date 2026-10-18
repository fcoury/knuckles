#!/usr/bin/env python3
"""Export a gated engineering-review package, never an approved assembly order."""
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMAGE='ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spacing',choices=['18.5','19.5'],default='18.5')
    p.add_argument('--hand',choices=['left','right'],required=True)
    a=p.parse_args();name='knuckles_integrated_'+a.hand
    routed=HERE/'output/routed'/a.spacing/a.hand;board=routed/(name+'.kicad_pcb')
    out=HERE/'output/manufacturing-review'/a.spacing/a.hand
    def rel(path):return str(path.relative_to(ROOT))
    def kicad(*args):
        subprocess.run(['docker','run','--rm','--platform','linux/amd64','-v',f'{ROOT}:/repo',
                        '-w','/repo',IMAGE,*args],cwd=ROOT,check=True)
    if not board.exists():raise RuntimeError('Route the board first')
    source=HERE/'output/integrated'/a.spacing/board.name
    kicad('python3','hardware/integrated-controller/check-routed.py',rel(source),rel(board))
    # Re-run the gate on the actual board, not a potentially stale summary.
    kicad('kicad-cli','pcb','drc','--format','json','-o',rel(routed/'drc.json'),rel(board))
    d=json.loads((routed/'drc.json').read_text())
    if d['unconnected_items']:raise RuntimeError('Manufacturing export refused: open connections')
    if any(v['severity']=='error' for v in d['violations']):raise RuntimeError('Manufacturing export refused: physical DRC errors')
    for script,report in [('check-reference.py','usb-reference.json'),('check-assembly.py','assembly.json')]:
        kicad('python3','hardware/integrated-controller/'+script,rel(board),rel(routed/report))
    out.mkdir(parents=True,exist_ok=True);gerbers=out/'gerbers';gerbers.mkdir(exist_ok=True)
    kicad('kicad-cli','pcb','export','gerbers','-l','F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts',
          '--subtract-soldermask','--exclude-value','-o',rel(gerbers)+'/',rel(board))
    kicad('kicad-cli','pcb','export','drill','--excellon-separate-th','--generate-map','--map-format','pdf','-o',rel(gerbers)+'/',rel(board))
    kicad('kicad-cli','pcb','export','pos','--format','csv','--units','mm','--side','both','--smd-only','--exclude-dnp','-o',rel(out/'kicad-positions.csv'),rel(board))
    # Scope PCBA to controller parts; keyboard switches/diodes are manual fit.
    parts=json.loads((HERE/'output/circuit.json').read_text())
    if isinstance(parts,dict):parts=parts['parts']
    parts=[x for x in parts if x['ref']!='J4' and (a.hand=='right' or x['ref'] not in {'J3','R4','R5'})]
    populate=[x for x in parts if not x['dnp'] and x['lcsc']]
    with (out/'controller-bom.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
        for x in populate:w.writerow([x['value'],x['ref'],x['footprint'],x['lcsc']])
    allowed={x['ref'] for x in populate}
    with (out/'kicad-positions.csv').open(newline='') as f:positions=list(csv.DictReader(f))
    if allowed!={row['Ref'] for row in positions if row['Ref'] in allowed}:raise RuntimeError('BOM and position references differ')
    with (out/'controller-cpl-review.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
        for row in positions:
            if row['Ref'] in allowed:
                w.writerow([row['Ref'],row['PosX'],row['PosY'],'Top' if row['Side']=='top' else 'Bottom',f"{float(row['Rot'])%360:.6f}"])
    (out/'README-REVIEW.md').write_text('''# Engineering review only - not approved for ordering

Gerbers and drill files passed the retained KiCad physical/connectivity gate.
This does not establish assembly orientation, impedance, power, RF or USB compliance.
CPL rotations are KiCad angles, pending comparison with the assembler's library
and pin-1/polarity preview on both sides. Do not submit them as approved rotations.
Keyboard switches/diodes, bare pogo/NTC pads and all DNP parts are excluded from
controller PCBA. R12 MUST remain unpopulated; charging remains disabled.

Outstanding gates: exact radio module procurement/consignment acceptance;
JLC04161H-3313 stack and controlled-impedance confirmation; DFM/stencil and via
tenting review; retained silkscreen/library warnings; physical touchpad/case and
battery clearances; current-limited bench bring-up and cell/NTC validation.
Use ENGINEERING.md for the bring-up sequence. No order or quote was submitted.
''')
    manifest={'board':rel(board),'sha256':hashlib.sha256(board.read_bytes()).hexdigest(),
              'physical_errors':0,'unconnected':0,'warnings':d['violations'],
              'manufacturing_release':False,'controller_population':[x['ref'] for x in populate],
              'dnp':[x['ref'] for x in parts if x['dnp']]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for source in [HERE/'references/stackup.json',HERE/'references/sourcing.json',HERE/'ENGINEERING.md',routed/'drc.json',routed/'usb-reference.json',routed/'assembly.json']:
        shutil.copy2(source,out/source.name)
    with zipfile.ZipFile(out/'pcb-review.zip','w',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(gerbers.iterdir()):z.write(file,file.name)
    print('Engineering-review package:',out)

if __name__=='__main__':main()
