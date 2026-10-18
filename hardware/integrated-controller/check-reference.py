#!/usr/bin/env python3
"""Sample actual filled ground beneath fixed USB traces; report pair lengths.

Exclude 0.6 mm around the data-via transitions themselves, where the signal
anti-pad necessarily opens the reference plane. This checks sampled copper,
not field impedance, return inductance or USB electrical compliance.
"""
import json
import math
import sys
from pathlib import Path
import pcbnew as pcb

board=pcb.LoadBoard(sys.argv[1])
planes={layer:[z.GetFilledPolysList(layer) for z in board.Zones()
               if not z.GetIsRuleArea() and z.GetNetname()=='GND' and z.GetLayer()==layer]
        for layer in [pcb.In1_Cu,pcb.In2_Cu]}
usb={'USB_DP','USB_DN','USB_MCU_DP','USB_MCU_DN'}
vias=[t for t in board.GetTracks() if isinstance(t,pcb.PCB_VIA) and t.GetNetname() in usb]
lengths={};missing=[];samples=0
for t in board.GetTracks():
    if isinstance(t,pcb.PCB_VIA) or t.GetNetname() not in usb:continue
    lengths[t.GetNetname()]=lengths.get(t.GetNetname(),0)+pcb.ToMM(t.GetLength())
    layer=pcb.In1_Cu if t.GetLayer()==pcb.F_Cu else pcb.In2_Cu
    a=t.GetStart();b=t.GetEnd();n=max(1,math.ceil(pcb.ToMM(t.GetLength())/.1))
    for i in range(n+1):
        f=i/n;x=round(a.x+(b.x-a.x)*f);y=round(a.y+(b.y-a.y)*f);v=pcb.VECTOR2I(x,y)
        if any((v-via.GetPosition()).EuclideanNorm()<pcb.FromMM(.6) for via in vias):continue
        samples+=1
        if not any(s.Contains(v) for s in planes[layer]):missing.append([pcb.ToMM(x),pcb.ToMM(y),board.GetLayerName(layer)])
result={'board':Path(sys.argv[1]).name,'sample_interval_mm':.1,'data_via_exclusion_radius_mm':.6,
        'samples':samples,'unreferenced_samples':missing,'track_length_mm':{k:round(v,3) for k,v in lengths.items()},
        'limitation':'Sampled ground coverage only; not an impedance or USB compliance simulation'}
Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(f'USB reference: {samples} samples, {len(missing)} outside filled ground')
assert not missing,missing[:10]
