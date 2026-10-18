#!/usr/bin/env python3
"""Compose dedicated keyboard halves from Ergogen mechanics and controller nets.

Run in pinned KiCad 8. Outputs are unrouted integration studies, not Gerbers.
"""
import argparse
from copy import deepcopy
import json
import shutil
import re
import tempfile
from pathlib import Path
import pcbnew as pcb
from circuit import PARTS, HERE
import keyboard_schematic

# Relative to the controller bay's upper-left corner. Angles describe actual
# component rotations, never mirrored pad geometry. B-side parts are <=1.5mm tall.
PLACEMENT = {
    'U1': (10,47,270), 'J1': (9,3.1,180), 'U4': (9,10.5,180),
    'R1': (3,7,90), 'R2': (15,7,90), 'C13': (9,14,0),
    'J3': (15,13.5,90), 'U2': (5,18,0), 'C4': (8.5,18,90),
    'C5': (1.5,18,90), 'C6': (5,14.5,0), 'Q3': (14,20,0),
    'R11': (15,16,0), 'R12': (12,16,90), 'R10': (14,24,0),
    'R6': (1.5,14,90), 'R7': (2,21,0), 'R8': (5,21,0),
    'R9': (9,21,0), 'SW2': (4,10.5,0), 'J2': (8,26.5,90),
    'U3': (5,37,0), 'L1': (5,33,0), 'C8': (1.5,37,90),
    'C9': (5,40,0), 'C10': (8.5,37,90), 'C11': (8.5,40,0),
    'R13': (1.5,40,0), 'SW1': (16.5,36,0),
    'C2': (.5,46,90), 'C1': (.5,50,90), 'C3': (3,53,0),
    'R18': (7,54,90), 'R19': (10,54,90),
    'R4': (15,3,90), 'R5': (15,10,90), 'J6': (14,31,0),
    'J5': (9,11,0), 'Q1': (5,19,0), 'Q2': (5,25,0),
    'R3': (12,39,0), 'R14': (5,15,0), 'R15': (9,19,90), 'R16': (9,23,90),
    'R17': (5,29,0), 'C12': (9,27,90),
}
BACK = {'J5','J6','Q1','Q2','Q3','R1','R2','R3','R4','R5','R10','R11','R12',
        'R14','R15','R16','R17','C12','C2','C3','R18','R19'}
TOUCHPAD_ONLY = {'J3','R4','R5'}

def vec(x,y): return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))

def compose(source, out, hand):
    # Ergogen emits one-line board segments for nice!nano socket jumpers.
    # Remove socket traces before importing the new controller.
    raw=(source/'pcbs/knuckles_wireless.kicad_pcb').read_text()
    raw=re.sub(r'^\s*\((?:segment|via) [^\n]*\)\s*$', '', raw, flags=re.M)
    assert '(segment ' not in raw and '(via ' not in raw and '(zone ' not in raw
    with tempfile.NamedTemporaryFile(suffix='.kicad_pcb',mode='w') as f:
        f.write(raw);f.flush();board=pcb.LoadBoard(f.name)
    anchors=json.loads((source/'integration-anchors.json').read_text())
    origin=anchors['controller_origin']
    # Keep front switch/diode footprints and the five main case mounting holes.
    # Controller-cover holes are replaced by a case-mounted touchpad support.
    for fp in list(board.GetFootprints()):
        kind=str(fp.GetFPID().GetLibItemName())
        keep=(kind in {'CPG1316S01D02','diode_tht_sod123'} and fp.GetLayer()==pcb.F_Cu)
        keep|=(kind=='mounting_hole_npth' and fp.GetReference() not in {'MH1','MH2'})
        keep|=kind=='knuckles_artwork_wordmark'
        # KiCad 8 Remove() transfers ownership to Python; destroying these
        # wrappers corrupts subsequent SWIG type conversions in this image.
        # Keep detached native objects alive for this short-lived process.
        if not keep: board.RemoveNative(fp)
    # Vendor the actual generated front-side lands so schematic updates can
    # resolve them without a user-specific global footprint library table.
    for fp in board.GetFootprints():
        kind=str(fp.GetFPID().GetLibItemName())
        if kind in {'CPG1316S01D02','diode_tht_sod123'}:
            copy=fp.Duplicate();copy.SetPosition(vec(0,0));copy.SetOrientationDegrees(0)
            pcb.FootprintSave(str(HERE/'libraries/Knuckles.pretty'),copy)
            fp.SetFPID(pcb.LIB_ID('Knuckles',kind))
    axis=anchors['mirror_axis_x']
    if hand=='right':
        for drawing in board.GetDrawings():drawing.Flip(vec(axis,0),True)
        for fp in board.GetFootprints():
            pos=fp.GetPosition()
            fp.SetPosition(vec(2*axis-pcb.ToMM(pos.x),pcb.ToMM(pos.y)))
            fp.SetOrientationDegrees(-fp.GetOrientationDegrees())
    board.GetDesignSettings().SetCopperLayerCount(4)
    board.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6))
    nets={str(n.GetNetname()):n for n in board.GetNetsByNetcode().values()}
    selected=deepcopy([p for p in PARTS if p['ref']!='J4' and (hand=='right' or p['ref'] not in TOUCHPAD_ONLY)])
    if hand=='left':
        module=next(p for p in selected if p['ref']=='U1')
        for pin in ['41','44']:module['nets'].pop(pin)
    for name in sorted({n for p in selected for n in p['nets'].values()}):
        if name not in nets:
            net=pcb.NETINFO_ITEM(board,name);board.Add(net);nets[name]=net
    for p in selected:
        fp=pcb.FootprintLoad(str(HERE/'libraries/Knuckles.pretty'),p['footprint'])
        fp.SetReference(p['ref']);fp.SetValue(p['value'])
        fp.SetFPID(pcb.LIB_ID('Knuckles',p['footprint']))
        board.Add(fp)
        x,y,angle=PLACEMENT[p['ref']]
        x+=origin[0];y+=origin[1]
        if hand=='right':x=2*axis-x;angle=-angle
        fp.SetPosition(vec(x,y));fp.SetOrientationDegrees(angle)
        if p['ref']=='SW1' and hand=='right':fp.SetOrientationDegrees(180)
        if p['ref'] in BACK:fp.Flip(fp.GetPosition(),True)
        for pad in fp.Pads():
            if pad.GetNumber() in p['nets']:pad.SetNet(nets[p['nets'][pad.GetNumber()]])
        fp.Reference().SetLayer(pcb.B_Fab if p['ref'] in BACK else pcb.F_Fab)
        fp.Reference().SetTextSize(vec(.7,.7));fp.Reference().SetTextThickness(pcb.FromMM(.12))
        if p['dnp']:fp.SetAttributes(fp.GetAttributes()|pcb.FP_EXCLUDE_FROM_BOM|pcb.FP_EXCLUDE_FROM_POS_FILES)
    # Widen the module's all-layer antenna keepout to the inner board edge.
    x0,x1=origin[0]+14,origin[0]+24
    if hand=='right':x0,x1=2*axis-x1,2*axis-x0
    y0,y1=origin[1]+41.5,origin[1]+52.5
    zone=pcb.ZONE(board);zone.SetIsRuleArea(True);zone.SetLayerSet(pcb.LSET.AllCuMask(4))
    zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True);zone.SetDoNotAllowPads(True)
    zone.SetDoNotAllowCopperPour(True);zone.SetDoNotAllowFootprints(False)
    zone.Outline().NewOutline()
    for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:zone.Outline().Append(pcb.FromMM(x),pcb.FromMM(y))
    board.Add(zone)
    name='knuckles_integrated_'+hand
    out.mkdir(parents=True,exist_ok=True)
    keyboard_schematic.write(out,name,board,selected)
    pcb.SaveBoard(str(out/(name+'.kicad_pcb')),board)
    project=json.loads((HERE.parents[1]/'kicad/projects/knuckles_wireless.kicad_pro').read_text())
    project['meta']['filename']=name+'.kicad_pro'
    (out/(name+'.kicad_pro')).write_text(json.dumps(project,indent=2)+'\n')
    (out/'fp-lib-table').write_text('(fp_lib_table (lib (name "Knuckles") (type "KiCad") (uri "${KIPRJMOD}/../../../libraries/Knuckles.pretty") (options "") (descr "Controller footprints")))\n')
    # Validate exact physical matrix and controller connections, independently
    # of placement and hand mirroring, before accepting generated output.
    switches=[f for f in board.GetFootprints() if str(f.GetFPID().GetLibItemName())=='CPG1316S01D02']
    diodes=[f for f in board.GetFootprints() if str(f.GetFPID().GetLibItemName())=='diode_tht_sod123']
    assert len(switches)==len(diodes)==27
    assert len({f.GetReference() for f in board.GetFootprints()})==len(list(board.GetFootprints()))
    for p in selected:
        fp=board.FindFootprintByReference(p['ref'])
        for pin,net in p['nets'].items():
            assert any(pad.GetNumber()==pin and pad.GetNetname()==net for pad in fp.Pads()),(hand,p['ref'],pin,net)
    metadata={'hand':hand,'spacing_mm':anchors['spacing_mm'],'controller_origin':origin,
              'mirror_axis_x':axis,'switch_count':27,'controller_components':len(selected),
              'copper_layers':4,'routed':False,'antenna_keepout':[x0,y0,x1,y1],
              'touchpad_center_y':origin[1]+11,'touchpad_width_mm':46.96,'touchpad_length_mm':43.95,
              'touchpad_placement':'Proposed 7mm forward shift; physical fit needs verification',
              'battery_placement':'External pack; keep clear of the antenna region on either side of PCB'}
    (out/(name+'.json')).write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'{name}: 27 keys, {len(selected)} controller parts, 4 copper layers; UNROUTED')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    for hand in ('left','right'):compose(args.source,args.output,hand)
