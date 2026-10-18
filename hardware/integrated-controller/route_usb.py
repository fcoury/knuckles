"""Locked USB route for the 18.5/19.5 left and right controllers.

3313 stack, 0.1356mm traces and 0.1501mm gap on the long coupled run.
Connector duplicate-pin stubs and package fanouts necessarily spread the pair.
"""
import pcbnew as pcb

def vec(x,y):return pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y))

def route(board,hand):
    # The bay is identical relative to U3 for both selectable key spacings.
    cx=pcb.ToMM(board.FindFootprintByReference('U3').GetPosition().x)
    off=cx-(113.568 if hand=='right' else 105.568)
    dy=pcb.ToMM(board.FindFootprintByReference('U3').GetPosition().y)-90.0
    def point(x,y):return vec(x+off,y+dy)
    nets={str(n.GetNetname()):n for n in board.GetNetsByNetcode().values()}
    def track(net,points,width=.1356,layer=pcb.F_Cu):
        for a,b in zip(points,points[1:]):
            if a==b:continue
            t=pcb.PCB_TRACK(board);t.SetStart(point(*a));t.SetEnd(point(*b));t.SetLayer(layer)
            t.SetWidth(pcb.FromMM(width));t.SetNet(nets[net]);t.SetLocked(True);board.Add(t)
    def via(net,x,y,diameter=.45,drill=.2):
        v=pcb.PCB_VIA(board);v.SetPosition(point(x,y));v.SetWidth(pcb.FromMM(diameter));v.SetDrill(pcb.FromMM(drill))
        v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNet(nets[net]);v.SetLocked(True);board.Add(v)
    def place(ref,x,y):
        fp=board.FindFootprintByReference(ref)
        if fp.GetLayer()==pcb.B_Cu:fp.Flip(fp.GetPosition(),True)
        fp.SetPosition(point(x,y));fp.SetOrientationDegrees(-90)
        fp.Reference().SetLayer(pcb.F_Fab)
    if hand=='right':
        place('R18',113.1,93.6);place('R19',115.0,93.6)
    else:
        for ref,x in [('R18',106.068),('R19',104.368)]:
            fp=board.FindFootprintByReference(ref);fp.SetPosition(point(x,108.4))
            fp.SetOrientationDegrees(90)
            p2=next(p for p in fp.Pads() if p.GetNumber()=='2')
            if p2.GetPosition().y > fp.GetPosition().y:fp.SetOrientationDegrees(-90)
        r7=board.FindFootprintByReference('R7');r7.SetPosition(point(103.568,88.0))
        c3=board.FindFootprintByReference('C3');c3.SetPosition(point(101.568,107.0))
    reset=board.FindFootprintByReference('SW2');reset.SetPosition(point(115.2,65.4))
    irq_pull=board.FindFootprintByReference('R6');irq_pull.SetPosition(point(117.2,78.0))
    gx,gy=(118.1,66.475) if hand=='right' else (116.5,67.3)
    track('GND',[(117.275,66.475),(gx,gy)],.25)
    via('GND',gx,gy,.6,.3)
    track('VBUS',[(108.793,68),(108.268,68),(108.268,67)],.25)
    via('VBUS',108.268,67,.6,.3)
    vbus_path=[(108.268,67),(114.6,67),(114.6,69.4),(115.3,69.4),(115.8,69.9)] if hand=='right' else [(108.268,67),(108.768,67),(108.768,69.9),(107.8,69.9)]
    track('VBUS',vbus_path,.3,pcb.In2_Cu)
    irq_pad=next(p for p in irq_pull.Pads() if p.GetNetname()=='CHG_INT_N')
    irq_y=pcb.ToMM(irq_pad.GetPosition().y)-dy
    irq_x=115.7 if hand=='right' else 108.118
    track('CHG_INT_N',[(irq_x,71.6),(irq_x,72),(118.1,72),(118.1,irq_y),(117.2,irq_y)],.15)
    # Interleaved A/B data pins merge through short, staggered via stubs.
    for net,x,y in [('USB_DP',108.818,62.35),('USB_DP',109.818,62.35),
                    ('USB_DN',109.318,59.95),('USB_DN',110.318,59.95)]:
        track(net,[(x,61.145),(x,y)]);via(net,x,y)
    track('USB_DP',[(109.818,62.35),(108.818,62.35),(108.818,65.45),(107.3,65.45)],layer=pcb.B_Cu)
    track('USB_DN',[(110.318,59.95),(107.3,59.95),(107.3,63.55)],layer=pcb.B_Cu)
    # Both flow-through pins are tied on the PCB, so physical connectivity does
    # not depend on a schematic assumption about an IC's internal connection.
    for net,y in [('USB_DP',65.45),('USB_DN',63.55)]:
        via(net,107.3,y);track(net,[(107.3,y),(111.9,y)]);via(net,111.9,y)
    track('GND',[(110.705,64.5),(112.0,64.5)],.25);via('GND',112.0,64.5,.6,.3)
    track('VBUS',[(108.43,64.5),(106.9,64.5)],.25);via('VBUS',106.9,64.5,.6,.3)
    # Long pair runs on B.Cu. In2 must remain a ground reference beneath this
    # corridor; a dedicated In2 ground zone is added below.
    if hand=='right':
        track('USB_DP',[(111.9,65.45),(113.0,65.45),(113.9,66.35),(116.6,66.35),
                        (116.6,90.0),(112.8,90.0),(112.0,90.8),(112.0,93.1)],layer=pcb.B_Cu)
        track('USB_DN',[(111.9,63.55),(113.2856,63.55),(115.8,66.0644),(116.8857,66.0644),
                        (116.8857,90.2857),(115.5,90.2857),(114.7,91.0857),(114.7,91.8)],layer=pcb.B_Cu)
        via('USB_DP',112.0,93.1);via('USB_DN',114.7,91.8)
        track('USB_DP',[(112.0,93.1),(112.325,92.775),(113.1,92.775)])
        track('USB_DN',[(114.7,91.8),(114.7,92.475),(115.0,92.775)])
        track('TPS_SCL',[(109.918,96.35),(109.918,95.8),(108.9,95.3)],.15)
        via('TPS_SCL',108.9,95.3,.6,.3)
        # Series resistors remain close to the MCU's USB lands, with short fanouts.
        track('USB_MCU_DP',[(113.1,94.425),(113.1,95.0),(113.918,95.818),(113.918,96.35)])
        track('USB_MCU_DN',[(115.0,94.425),(115.0,94.7),(114.718,94.982),(114.718,96.35)])
    else:
        def left_track(net,points,layer=pcb.B_Cu):
            track(net,[(x-102.432,y) for x,y in points],layer=layer)
        def left_via(net,x,y):via(net,x-102.432,y)
        left_track('USB_DP',[(214.332,65.45),(215.432,65.45),(216.332,66.35),(219.9,66.35),
                            (219.9,86.5),(214.0,86.5),(212.0,88.5),(212.0,111.0),
                            (208.5,111.0),(208.5,109.225)])
        left_track('USB_DN',[(214.332,63.55),(215.7176,63.55),(218.232,66.0644),(220.1857,66.0644),
                            (220.1857,86.7857),(214.1183,86.7857),(212.2857,88.6183),
                            (212.2857,111.2857),(206.8,111.2857),(206.8,109.225)])
        # Series output goes through a short via fanout to the module's south
        # USB lands. Handedness changes these lands, never their pin numbers.
        left_via('USB_MCU_DP',207.65,106.9);left_via('USB_MCU_DN',206.85,106.9)
        left_track('USB_MCU_DP',[(208.5,107.575),(208.325,107.575),(207.65,106.9)])
        left_track('USB_MCU_DN',[(206.8,107.575),(206.85,107.525),(206.85,106.9)])
        left_track('USB_MCU_DP',[(207.65,106.9),(207.65,105.65)],pcb.F_Cu)
        left_track('USB_MCU_DN',[(206.85,106.9),(206.85,105.65)],pcb.F_Cu)
    # Reference plane under B.Cu pair. Power distribution remains in the
    # controller interior; no isolated power island is used as a USB reference.
    z=pcb.ZONE(board);z.SetLayer(pcb.In2_Cu);z.SetNet(nets['GND']);z.SetLocalClearance(pcb.FromMM(.2))
    z.SetPadConnection(pcb.ZONE_CONNECTION_FULL);z.Outline().NewOutline()
    box=board.GetBoardEdgesBoundingBox()
    for x,y in [(box.GetLeft(),box.GetTop()),(box.GetRight(),box.GetTop()),
                (box.GetRight(),box.GetBottom()),(box.GetLeft(),box.GetBottom())]:z.Outline().Append(x,y)
    board.Add(z)
    return {'stage':'locked-'+hand+'-usb','complete':True,'width_mm':.1356,'gap_mm':.1501,
            'long_run_layer':'B.Cu','reference_layer':'In2.Cu',
            'reference_condition':'Verify ground remains continuous under the pair after all power/signal routing',
            'via_mm':{'diameter':.45,'drill':.2},'series_resistors':('F.Cu' if hand=='right' else 'B.Cu')+' near MCU, 27 ohm'}
