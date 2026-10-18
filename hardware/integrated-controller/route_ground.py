"""Explicit ground-pad stitching; also safe to apply to an imported candidate."""
import sys
import pcbnew as pcb

def route(board,hand):
    net=next(n for n in board.GetNetsByNetcode().values() if n.GetNetname()=='GND')
    def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))
    def track(points):
        for a,b in zip(points,points[1:]):
            av=vec(*a);bv=vec(*b)
            if any(not isinstance(t,pcb.PCB_VIA) and t.GetNetname()=='GND' and t.GetLayer()==pcb.F_Cu
                   and (t.GetStart()-av).EuclideanNorm()<2000 and (t.GetEnd()-bv).EuclideanNorm()<2000 for t in board.GetTracks()):continue
            t=pcb.PCB_TRACK(board);t.SetStart(av);t.SetEnd(bv);t.SetWidth(pcb.FromMM(.2))
            t.SetLayer(pcb.F_Cu);t.SetNet(net);t.SetLocked(True);board.Add(t)
    def via(x,y):
        v=vec(x,y)
        if any(isinstance(t,pcb.PCB_VIA) and t.GetNetname()=='GND' and (t.GetPosition()-v).EuclideanNorm()<2000 for t in board.GetTracks()):return
        t=pcb.PCB_VIA(board);t.SetPosition(v);t.SetWidth(pcb.FromMM(.6));t.SetDrill(pcb.FromMM(.3))
        t.SetViaType(pcb.VIATYPE_THROUGH);t.SetLayerPair(pcb.F_Cu,pcb.B_Cu);t.SetNet(net);t.SetLocked(True);board.Add(t)
    def pad(ref,num):
        p=next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber()==num)
        assert p.GetNetname()=='GND',(ref,num)
        return pcb.ToMM(p.GetPosition().x),pcb.ToMM(p.GetPosition().y)
    x,y=pad('C13','2');track([(x,y),(x,y-1.7)]);via(x,y-1.7)
    x,y=pad('SW2','3');track([(x,y),(x-1.125,y-.225)]);via(x-1.125,y-.225)
    x,y=pad('C1','2')
    other=next(p for p in board.FindFootprintByReference('C1').Pads() if p.GetNumber()=='1')
    vy=y+(1.175 if y>pcb.ToMM(other.GetPosition().y) else -1.175)
    track([(x,y),(x,vy)]);via(x,vy)
    x,y=pad('SW1','1')
    vx=x-2.2;vy=y-(.75 if hand=='left' else .3)
    points=[(x,y),(x-1,y),(vx,vy)] if hand=='left' else [(x,y),(x,vy),(vx,vy)]
    track(points);via(vx,vy)
    if hand=='right':
        x,y=pad('J3','2');track([(x,y),(x-1.668,y)]);via(x-1.668,y)
    # The three grounds beside the antenna need a route into the body ground
    # region; copper slivers along the keepout alone are not a reliable tie.
    module=board.FindFootprintByReference('U1');m=module.GetPosition()
    mx=pcb.ToMM(m.x);my=pcb.ToMM(m.y);s=1 if hand=='right' else -1
    def point(x,y):return mx+s*x,my+s*y
    track([point(-3.75,-4.65),point(-3.75,-5.8),point(-2.968,-5.8)])
    track([point(-3.75,4.65),point(-2.65,4.65)])
    track([point(-3.75,4.65),point(-3.75,5.8),point(-2.568,5.8)])
    for xy in [point(-2.968,-5.8),point(-2.568,5.8)]:via(*xy)
    if hand=='left':finish_left(board)


def finish_left(board):
    """Tie the module corner ground and back-side bypass ground into the planes."""
    def pad(ref,num):return next(p for p in board.FindFootprintByReference(ref).Pads() if p.GetNumber()==num)
    def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))
    net=pad('C1','2').GetNet()
    def track(points,layer):
        for a,b in zip(points,points[1:]):
            if a==b:continue
            t=pcb.PCB_TRACK(board);t.SetStart(vec(*a));t.SetEnd(vec(*b));t.SetLayer(layer)
            t.SetWidth(pcb.FromMM(.2));t.SetNet(net);t.SetLocked(True);board.Add(t)
    p=pad('U1','15');x=pcb.ToMM(p.GetPosition().x);y=pcb.ToMM(p.GetPosition().y)
    r13=pad('R13','2').GetPosition();gx=pcb.ToMM(r13.x)-.525;gy=pcb.ToMM(r13.y)+1
    track([(x,y),(x,y-.7),(gx,gy)],pcb.F_Cu)
    c2=pad('C2','2').GetPosition();x2=pcb.ToMM(c2.x);y2=pcb.ToMM(c2.y)
    track([(x2,y2),(x2,y2-1.35)],pcb.B_Cu)
    via=pcb.PCB_VIA(board);via.SetPosition(vec(x2,y2-1.35));via.SetWidth(pcb.FromMM(.6));via.SetDrill(pcb.FromMM(.3))
    via.SetViaType(pcb.VIATYPE_THROUGH);via.SetLayerPair(pcb.F_Cu,pcb.B_Cu);via.SetNet(net);via.SetLocked(True);board.Add(via)

if __name__=='__main__':
    board=pcb.LoadBoard(sys.argv[1]);route(board,sys.argv[2])
    pcb.ZONE_FILLER(board).Fill(board.Zones());pcb.SaveBoard(sys.argv[1],board)
