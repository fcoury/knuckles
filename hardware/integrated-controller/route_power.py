"""Deterministic, constrained local power routing for the integrated keyboards.

This is a reviewed routing cell, not an autorouter. Coordinates are relative
 to U3; the same physical cell is placed on either hand without mirroring pads.
Unrouted external connections remain explicit and no fabrication files result.
"""
import pcbnew as pcb


def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))

def route(board,hand):
    u3=board.FindFootprintByReference('U3')
    cx=pcb.ToMM(u3.GetPosition().x);cy=pcb.ToMM(u3.GetPosition().y)-1
    dy=cy-90.0
    def place(ref,x,y,angle):
        fp=board.FindFootprintByReference(ref)
        fp.SetPosition(vec(cx+x,cy+y));fp.SetOrientationDegrees(angle)
    # Short symmetric switch-node paths, input/output caps adjacent to U3.
    for ref,args in {
        'U3':(0,0,0),'L1':(-3.8,0,90),
        'C10':(-1.068,-3.4,90),'C11':(2.932,-3.4,90),
        'C8':(-2.768,3.5,-90),'C9':(3.432,0,0),
        # Make room above the power cell for the output capacitor returns.
    }.items():place(ref,*args)
    battery=board.FindFootprintByReference('J2')
    battery.SetPosition(vec(pcb.ToMM(battery.GetPosition().x),79.9+dy))
    # Match the charger pin sides instead of sending its input and battery
    # capacitor traces across each other. Fixed package orientation on both hands.
    u2=board.FindFootprintByReference('U2');u2.SetOrientationDegrees(0)
    ucx=pcb.ToMM(u2.GetPosition().x)
    for ref,x,angle in [('C5',ucx-3.5,-90),('C4',ucx+3.5,-90)]:
        fp=board.FindFootprintByReference(ref);fp.SetPosition(vec(x,72+dy));fp.SetOrientationDegrees(angle)
    fp=board.FindFootprintByReference('C6');fp.SetPosition(vec(ucx,68.5+dy));fp.SetOrientationDegrees(0)
    nets={str(n.GetNetname()):n for n in board.GetNetsByNetcode().values()}
    def track(net,points,width=.3,layer=pcb.F_Cu):
        for a,b in zip(points,points[1:]):
            if a==b:continue
            item=pcb.PCB_TRACK(board);item.SetStart(vec(cx+a[0],cy+a[1]));item.SetEnd(vec(cx+b[0],cy+b[1]))
            item.SetWidth(pcb.FromMM(width));item.SetLayer(layer);item.SetNet(nets[net]);item.SetLocked(True);board.Add(item)
    def via(net,x,y,diameter=.6,drill=.3):
        item=pcb.PCB_VIA(board);item.SetPosition(vec(cx+x,cy+y));item.SetWidth(pcb.FromMM(diameter));item.SetDrill(pcb.FromMM(drill))
        item.SetViaType(pcb.VIATYPE_THROUGH);item.SetLayerPair(pcb.F_Cu,pcb.B_Cu);item.SetNet(nets[net]);item.SetLocked(True);board.Add(item)
    # Switch paths leave the narrow IC lands at 0.3mm, widening outside the IC.
    track('SW_L2',[(-1.2125,-.5),(-1.95,-.5)],.3)
    track('SW_L2',[(-1.95,-.5),(-2.6,-1.15),(-3.8,-1.15)],.5)
    track('SW_L1',[(-1.2125,.5),(-1.95,.5)],.3)
    track('SW_L1',[(-1.95,.5),(-2.6,1.15),(-3.8,1.15)],.5)
    # Power input and quiet VINA bypass take separate branches from the input cap.
    track('SYS',[(-1.2125,1),(-1.2125,1.8),(-1.9625,2.55),(-2.768,2.55)],.3)
    track('SYS',[(-2.768,2.55),(-4.168,2.55)],.4);via('SYS',-4.168,2.55)
    track('SYS',[(1.2125,0),(2.657,0)],.25)
    track('SYS',[(2.657,0),(2.657,1.5)],.25);via('SYS',2.657,1.5)
    # Quiet VINA feed crosses the resistor body corridor on F.Cu, then uses
    # a short inner-layer link away from the B.Cu USB reference corridor.
    track('SYS',[(-2.768,2.55),(-2.768,2.9),(-2.068,3.6),(.432,3.6)],.15)
    via('SYS',.432,3.6)
    track('SYS',[(.432,3.6),(1.732,3.6),(1.732,2.425),(2.657,1.5)],.25,pcb.In2_Cu)
    # VOUT goes straight to C10. Feedback takes the quiet capacitor node,
    # connected across to the second output cap, rather than a switch node.
    track('+3V3',[(-1.2125,-1),(-1.068,-1.1445),(-1.068,-2.45)],.3)
    track('+3V3',[(-1.068,-2.45),(2.932,-2.45)],.5);via('+3V3',1.5,-2.45)
    track('+3V3',[(1.2125,-1),(1.882,-1),(2.932,-2.05),(2.932,-2.45)],.25)
    # Pull-down is on the back to leave a USB landing corridor above the MCU.
    r13=board.FindFootprintByReference('R13');r13.SetPosition(vec(cx+(-2 if hand=='left' else 3.232),cy+3.9))
    r13.SetOrientationDegrees(0)
    rp={p.GetNumber():p for p in r13.Pads()}
    if rp['1'].GetPosition().x > r13.GetPosition().x:r13.SetOrientationDegrees(180)
    track('REG_EN',[(1.2125,1),(2.032,1),(2.032,1.9),(2.832,2.7),(2.832,3)],.2)
    via('REG_EN',2.832,3)
    x=pcb.ToMM(rp['1'].GetPosition().x)-cx
    if hand=='left':
        track('REG_EN',[(2.832,3),(2.832,5.6),(x,5.6),(x,3.9)],.2,pcb.B_Cu)
    else:
        track('REG_EN',[(2.832,3),(x,3+abs(2.832-x)),(x,3.9)],.2,pcb.B_Cu)
    x=pcb.ToMM(rp['2'].GetPosition().x)-cx
    gx=-1.7 if hand=='left' else 3.232
    gy=4.9 if hand=='left' else 4.95
    track('GND',[(x,3.9),(x,4.125),(gx,gy)],.3,pcb.B_Cu)
    via('GND',gx,gy)
    # Land-to-exposed-pad ground joins; external vias avoid the paste apertures.
    track('GND',[(-1.2125,0),(0,0)],.3)
    track('GND',[(1.2125,-.5),(0,-.5)],.25)
    track('GND',[(1.2125,.5),(0,.5)],.25)
    track('GND',[(0,-.5),(0,-1.6)],.4);via('GND',0,-1.6)
    track('GND',[(0,.5),(0,1.6)],.4);via('GND',0,1.6)
    for start,end in [((-1.068,-4.35),(.132,-4.35)),((2.932,-4.35),(4.032,-4.35)),
                      ((-2.768,4.45),(-5 if hand=='left' else -3.668,4.45)),
                      ((4.207,0),((5.5,-1) if hand=='left' else (4.207,1.3)))]:
        track('GND',[start,end],.3);via('GND',*end)
    # Charger: short input/battery/SYS capacitor loops and separate power feeds.
    track('SYS',[(-1.05,-18.8),(-1.8,-18.8),(-1.8,-19.2)],.15)
    track('SYS',[(-1.8,-19.2),(-.95,-20.05),(-.95,-21.5)],.35)
    track('SYS',[(-.95,-21.5),(-2.2,-21.5)],.4);via('SYS',-2.2,-21.5)
    track('SYS',[(-2.2,-21.5),(-5.8,-21.5),(-5.8,2.55),(-4.168,2.55)],.5,pcb.In2_Cu)
    track('VBUS',[(1.05,-18.8),(1.532,-18.8),(1.532,-19.35)],.15)
    track('VBUS',[(1.532,-19.35),(3.5,-19.35),(3.5,-20.1),(2.232,-20.1)],.4)
    via('VBUS',2.232,-20.1)
    track('VBAT',[(-1.05,-18.4),(-3.125,-18.4),(-3.5,-18.775)],.15)
    track('VBAT',[(-3.5,-18.775),(-3.5,-20.1)],.4)
    via('VBAT',-3.5,-20.1)
    track('GND',[(-1.05,-17.2),(0,-17.2)],.15)
    track('GND',[(0,-17.2),(0,-19.7),(.8,-19.7)],.3)
    via('GND',0,-19.7);via('GND',.8,-19.7)
    track('GND',[(.95,-21.5),(.95,-20.3),(.8,-20.15),(.8,-19.7)],.3)
    track('GND',[(.95,-21.5),(2.15,-21.5)],.3);via('GND',2.15,-21.5)
    track('GND',[(3.5,-17.225),(3.5,-15.9),(2.232,-15.9)],.3);via('GND',2.232,-15.9)
    track('GND',[(-3.5,-17.225),(-5,-17.225),(-5,-15.35)],.3)
    via('GND',-5,-15.35)
    # Left-side control vias spread around the back-side PMOS lands and keep
    # an open lane for SDA below SCL. Right-side back placement differs.
    # Fan out the fine-pitch control lands before general routing. Power
    # necks turn upward, leaving these lanes clear of the capacitor returns.
    for net,points,end in [
        ('CHG_PG_N',[(-1.05,-18),(-2.218,-18),(-2.318,-17.9)],(-2.318,-17.9)),
        ('CHG_EN_N',[(-1.05,-17.6),(-1.618,-17.6),(-2.318,-16.9),(-2.318,-16.15)],(-2.318,-16.15)),
        ('CHG_INT_N',[(1.05,-18.4),(2.55 if hand=='left' else 2.132,-18.4)],(2.55 if hand=='left' else 2.132,-18.4)),
        ('PMIC_SCL',[(1.05,-18),(2.0,-18),(2.232,-17.4)] if hand=='left' else [(1.05,-18),(1.582,-18),(2.132,-17.45),(2.132,-17.4)],(2.232 if hand=='left' else 2.132,-17.4)),
    ]:
        track(net,points,.15);via(net,*end,.45,.2)
    if hand=='left':
        track('PMIC_SDA',[(1.05,-17.6),(1.65,-17.6),(1.65,-17),(2.15,-16.65)],.15)
        via('PMIC_SDA',2.15,-16.65,.45,.2)
    module=board.FindFootprintByReference('U1')
    adc=next(p for p in module.Pads() if p.GetNumber()=='20')
    ax=pcb.ToMM(adc.GetPosition().x)-cx;ay=pcb.ToMM(adc.GetPosition().y)-cy
    direction=1 if adc.GetPosition().x>module.GetPosition().x else -1
    escape=1.0 if hand=='left' else 1.2
    track('BATT_ADC',[(ax,ay),(ax+direction*escape,ay)],.15)
    via('BATT_ADC',ax+direction*escape,ay)
    r14=board.FindFootprintByReference('R14')
    rbat=next(p for p in r14.Pads() if p.GetNetname()=='VBAT')
    rx=pcb.ToMM(rbat.GetPosition().x)-cx;ry=pcb.ToMM(rbat.GetPosition().y)-cy
    track('VBAT',[(rx,ry),(rx,-22.5),(-3.5,-22.5),(-3.5,-20.1)],.2,pcb.B_Cu)
    # Battery connector's large lands escape toward their inner board side.
    for pad in battery.Pads():
        if pad.GetNumber() not in ['1','2']:continue
        x=pcb.ToMM(pad.GetPosition().x)-cx;y=pcb.ToMM(pad.GetPosition().y)-cy
        net=pad.GetNetname()
        if net=='VBAT':
            escape_y=y+(2 if hand=='left' else -2)
            escape_x=x+(1.76 if hand=='left' else 1.56)
            track(net,[(x,y),(escape_x,escape_y)],.5);via(net,escape_x,escape_y)
            track(net,[(-3.5,-20.1),(-3.5,escape_y),(escape_x,escape_y)],.4,pcb.In2_Cu)
        else:
            track(net,[(x,y),(x+2.6,y)],.5);via(net,x+2.6,y)
        # The external battery feed will use outer-layer routing, keeping
        # In2 continuous under the USB pair.
    # Ground reference on In1 is continuous beneath the signal/power cell.
    # All-layer antenna rule areas automatically subtract their forbidden area.
    bbox=board.GetBoardEdgesBoundingBox()
    zone=pcb.ZONE(board);zone.SetLayer(pcb.In1_Cu);zone.SetNet(nets['GND']);zone.SetLocalClearance(pcb.FromMM(.2))
    zone.SetPadConnection(pcb.ZONE_CONNECTION_FULL)
    zone.Outline().NewOutline()
    for x,y in [(bbox.GetLeft(),bbox.GetTop()),(bbox.GetRight(),bbox.GetTop()),
                (bbox.GetRight(),bbox.GetBottom()),(bbox.GetLeft(),bbox.GetBottom())]:zone.Outline().Append(x,y)
    board.Add(zone)
    return {'stage':'regulator-and-charger-power','complete_board':False,'locked_tracks':True,
            'U3_center_mm':[cx,cy],'local_power_nets':['SW_L1','SW_L2','SYS','+3V3','GND','REG_EN'],
            'via_mm':{'diameter':.6,'drill':.3},'thermal_vias':'outside exposed-pad paste apertures',
            'remaining':'External power distribution, controller/charger control signals and matrix need the separate constrained routing stage'}
