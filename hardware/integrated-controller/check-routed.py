#!/usr/bin/env python3
"""Refill and verify the autorouter preserved fixed geometry and inner layers."""
import sys
from collections import Counter
import pcbnew as pcb

source=pcb.LoadBoard(sys.argv[1]);board=pcb.LoadBoard(sys.argv[2])
source_fp={f.GetReference():f for f in source.GetFootprints()}
after_fp={f.GetReference():f for f in board.GetFootprints()}
assert source_fp.keys()==after_fp.keys(),'Footprint references changed during routing'
for ref,fp in source_fp.items():
    other=after_fp[ref]
    assert (fp.GetPosition()-other.GetPosition()).EuclideanNorm()<2000,ref
    assert fp.GetLayer()==other.GetLayer() and abs(fp.GetOrientationDegrees()-other.GetOrientationDegrees())<.001,ref
    def pads(f):return Counter((p.GetNumber(),p.GetNetname()) for p in f.Pads())
    assert pads(fp)==pads(other),('Physical pad/net contract changed',ref)
    for pad in fp.Pads():
        assert any(q.GetNumber()==pad.GetNumber() and q.GetNetname()==pad.GetNetname()
                   and (q.GetPosition()-pad.GetPosition()).EuclideanNorm()<2000
                   for q in other.Pads()),('Pad geometry moved',ref,pad.GetNumber())
assert board.GetCopperLayerCount()==4

def signature(t):
    if isinstance(t,pcb.PCB_VIA):
        return ('via',t.GetNetname(),t.GetPosition().x,t.GetPosition().y,t.GetWidth(),t.GetDrillValue())
    a=(t.GetStart().x,t.GetStart().y);b=(t.GetEnd().x,t.GetEnd().y)
    return ('track',t.GetNetname(),t.GetLayer(),t.GetWidth(),*sorted([a,b]))
# KiCad's DSN exporter merges consecutive collinear locked segments. Check
# coverage geometrically rather than demanding identical segment boundaries.
def on_centerline(track,v):
    a=track.GetStart();b=track.GetEnd();dx=b.x-a.x;dy=b.y-a.y
    f=max(0,min(1,((v.x-a.x)*dx+(v.y-a.y)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
    return ((v.x-a.x-f*dx)**2+(v.y-a.y-f*dy)**2)**.5 < pcb.FromMM(.002)
existing=list(source.GetTracks());after=list(board.GetTracks())
for t in existing:
    if isinstance(t,pcb.PCB_VIA):
        assert any(u.GetNetname()==t.GetNetname() and (u.GetPosition()-t.GetPosition()).EuclideanNorm()<pcb.FromMM(.002) and abs(u.GetWidth()-t.GetWidth())<200 and abs(u.GetDrillValue()-t.GetDrillValue())<200 for u in after if isinstance(u,pcb.PCB_VIA)),signature(t)
        continue
    for f in [0,.25,.5,.75,1]:
        a=t.GetStart();b=t.GetEnd();v=pcb.VECTOR2I(round(a.x+(b.x-a.x)*f),round(a.y+(b.y-a.y)*f))
        assert any(not isinstance(u,pcb.PCB_VIA) and u.GetNetname()==t.GetNetname()
                   and u.GetLayer()==t.GetLayer() and abs(u.GetWidth()-t.GetWidth())<200
                   and on_centerline(u,v) for u in after),signature(t)
for t in after:
    if not isinstance(t,pcb.PCB_VIA) and t.GetLayer() in [pcb.In1_Cu,pcb.In2_Cu]:
        for f in [0,.25,.5,.75,1]:
            a=t.GetStart();b=t.GetEnd();v=pcb.VECTOR2I(round(a.x+(b.x-a.x)*f),round(a.y+(b.y-a.y)*f))
            assert any(not isinstance(u,pcb.PCB_VIA) and u.GetNetname()==t.GetNetname() and u.GetLayer()==t.GetLayer() and on_centerline(u,v) for u in existing),'Router added or changed an inner-layer track'
pcb.ZONE_FILLER(board).Fill(board.Zones())
pcb.SaveBoard(sys.argv[2],board)
print('Footprint/pad contracts, fixed power/USB route coverage and inner-layer restriction verified; zones refilled.')
