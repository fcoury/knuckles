#!/usr/bin/env python3
"""Reuse a validated controller's copper across spacing variants of one hand.

Run inside the pinned KiCad image. Footprints must have identical geometry
relative to U3. Matrix copper stays in the target; DRC/routing must resolve
any conflicts at the interface before accepting the result.
"""
import sys
import pcbnew as pcb
from circuit import PARTS

if len(sys.argv)<4:raise SystemExit('Usage: reuse-controller.py SOURCE TARGET NET [NET ...]')
source=pcb.LoadBoard(sys.argv[1]);target=pcb.LoadBoard(sys.argv[2])
delta=target.FindFootprintByReference('U3').GetPosition()-source.FindFootprintByReference('U3').GetPosition()
refs={p['ref'] for p in PARTS}
for f in source.GetFootprints():
    if f.GetReference() not in refs:continue
    other=target.FindFootprintByReference(f.GetReference())
    assert other and (f.GetPosition()+delta-other.GetPosition()).EuclideanNorm()<2000,f.GetReference()
    assert f.GetLayer()==other.GetLayer() and abs(f.GetOrientationDegrees()-other.GetOrientationDegrees())<.001,f.GetReference()

selected=set(sys.argv[3:])
def controller(net):return net in selected
for t in list(target.GetTracks()):
    if controller(t.GetNetname()):target.RemoveNative(t)
nets={n.GetNetname():n for n in target.GetNetsByNetcode().values()}
count=0
for t in source.GetTracks():
    if not controller(t.GetNetname()):continue
    if isinstance(t,pcb.PCB_VIA):
        c=pcb.PCB_VIA(target);c.SetPosition(t.GetPosition()+delta);c.SetWidth(t.GetWidth());c.SetDrill(t.GetDrillValue())
        c.SetViaType(pcb.VIATYPE_THROUGH);c.SetLayerPair(pcb.F_Cu,pcb.B_Cu)
    else:
        assert t.GetClass()=='PCB_TRACK'
        c=pcb.PCB_TRACK(target);c.SetStart(t.GetStart()+delta);c.SetEnd(t.GetEnd()+delta)
        c.SetWidth(t.GetWidth());c.SetLayer(t.GetLayer())
    c.SetNet(nets[t.GetNetname()]);c.SetLocked(True);target.Add(c);count+=1
pcb.ZONE_FILLER(target).Fill(target.Zones());pcb.SaveBoard(sys.argv[2],target)
print(f'Reused {count} controller tracks/vias; matrix interface requires DRC and rerouting.')
