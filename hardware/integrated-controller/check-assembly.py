#!/usr/bin/env python3
"""Flag ordinary via holes that enter a solder-paste pad on either face."""
import json
import sys
from pathlib import Path
import pcbnew as pcb

board=pcb.LoadBoard(sys.argv[1]);hits=[]
for via in board.GetTracks():
    if not isinstance(via,pcb.PCB_VIA):continue
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if not any(pad.GetLayerSet().Contains(l) for l in [pcb.F_Paste,pcb.B_Paste]):continue
            if pad.HitTest(via.GetPosition(),via.GetDrillValue()//2):
                hits.append({'reference':fp.GetReference(),'pad':pad.GetNumber(),
                             'net':via.GetNetname(),'x_mm':pcb.ToMM(via.GetPosition().x),
                             'y_mm':pcb.ToMM(via.GetPosition().y)})
result={'via_holes_intersecting_paste_pads':hits,'manufacturing_release':False,
        'limitation':'Pad-shape screen only; assembler must review stencil apertures, thermal vias and tenting.'}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(f'Assembly screen: {len(hits)} via holes intersect paste pads')
assert not hits,hits[:10]
