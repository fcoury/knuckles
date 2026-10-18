"""Fixed finishing routes for the narrower left controller bay."""
import json
from pathlib import Path
import pcbnew as pcb

def route(board,hand,spacing):
    if hand!='left' or spacing!=18.5:return {'applied':False}
    data=json.loads((Path(__file__).parent/'references/left-18.5-finishing-routes.json').read_text())
    origin=board.FindFootprintByReference('U3').GetPosition()
    def point(xy):return origin+pcb.VECTOR2I(pcb.FromMM(xy[0]),pcb.FromMM(xy[1]))
    nets={n.GetNetname():n for n in board.GetNetsByNetcode().values()}
    for row in data['tracks']:
        t=pcb.PCB_TRACK(board);t.SetStart(point(row['start_mm']));t.SetEnd(point(row['end_mm']))
        t.SetWidth(pcb.FromMM(row['width_mm']));t.SetLayer(board.GetLayerID(row['layer']))
        t.SetNet(nets[row['net']]);t.SetLocked(True);board.Add(t)
    for row in data['vias']:
        t=pcb.PCB_VIA(board);t.SetPosition(point(row['position_mm']));t.SetWidth(pcb.FromMM(row['diameter_mm']));t.SetDrill(pcb.FromMM(row['drill_mm']))
        t.SetViaType(pcb.VIATYPE_THROUGH);t.SetLayerPair(pcb.F_Cu,pcb.B_Cu);t.SetNet(nets[row['net']]);t.SetLocked(True);board.Add(t)
    return {'applied':True,'inner_signal':'C1 on In2.Cu, west of USB reference corridor','source':'references/left-18.5-finishing-routes.json'}
