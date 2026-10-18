"""Run with KiCad 8 pcbnew: produce an explicitly unrouted placement draft."""
import json
from pathlib import Path
import pcbnew

HERE=Path(__file__).resolve().parent
OUT=HERE/'output'
parts=json.loads((OUT/'circuit.json').read_text())
board=pcbnew.BOARD()
board.SetFileName(str(OUT/'knuckles_controller.kicad_pcb'))
board.GetDesignSettings().SetCopperLayerCount(2)
board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.6))
nets={}
for name in sorted({net for p in parts for net in p['nets'].values()}):
    net=pcbnew.NETINFO_ITEM(board,name)
    board.Add(net);nets[name]=net

for p in parts:
    fp=pcbnew.FootprintLoad(str(HERE/'libraries/Knuckles.pretty'),p['footprint'])
    if fp is None:raise RuntimeError('Missing footprint: '+p['footprint'])
    fp.SetReference(p['ref']);fp.SetValue(p['value'])
    fp.SetFPID(pcbnew.LIB_ID('Knuckles',p['footprint']))
    board.Add(fp)
    pads={pad.GetNumber() for pad in fp.Pads() if pad.GetNumber()}
    missing=set(p['nets'])-pads
    if missing:raise RuntimeError(f'{p["ref"]}: symbol nets missing physical pads {missing}')
    for pad in fp.Pads():
        net=p['nets'].get(pad.GetNumber())
        if net:pad.SetNet(nets[net])
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(p['pcb'][0]),pcbnew.FromMM(p['pcb'][1])))
    fp.SetOrientationDegrees(p['pcb'][2])
    fp.Reference().SetVisible(True)
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
    fp.Reference().SetTextThickness(pcbnew.FromMM(.12))
    if p['dnp']:fp.SetAttributes(fp.GetAttributes()|pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_EXCLUDE_FROM_POS_FILES)

for start,end in [((0,0),(45,0)),((45,0),(45,55)),((45,55),(0,55)),((0,55),(0,0))]:
    edge=pcbnew.PCB_SHAPE();edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(start[0]),pcbnew.FromMM(start[1])))
    edge.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(end[0]),pcbnew.FromMM(end[1])))
    edge.SetLayer(pcbnew.Edge_Cuts);edge.SetWidth(pcbnew.FromMM(.05));board.Add(edge)
# Keep all copper and components out of the antenna strip, on both layers.
zone=pcbnew.ZONE(board);zone.SetIsRuleArea(True)
zone.SetLayerSet(pcbnew.LSET.AllCuMask(2))
zone.SetDoNotAllowTracks(True);zone.SetDoNotAllowVias(True);zone.SetDoNotAllowCopperPour(True)
zone.SetDoNotAllowPads(True);zone.SetDoNotAllowFootprints(False)
zone.Outline().NewOutline()
for x,y in [(0,0),(45,0),(45,4.05),(0,4.05)]:zone.Outline().Append(pcbnew.FromMM(x),pcbnew.FromMM(y))
board.Add(zone)
for text,pos,layer in [('KNUCKLES CTRL 0.2',(22.5,18.5),pcbnew.F_Fab),('UNROUTED ENGINEERING DRAFT',(22.5,7),pcbnew.B_SilkS),('ANTENNA: NO COPPER / BATTERY / METAL',(22.5,2),pcbnew.Dwgs_User)]:
    t=pcbnew.PCB_TEXT(board);t.SetText(text);t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(pos[0]),pcbnew.FromMM(pos[1])))
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)));t.SetTextThickness(pcbnew.FromMM(.12));t.SetLayer(layer);board.Add(t)
pcbnew.SaveBoard(str(OUT/'knuckles_controller.kicad_pcb'),board)
print(f'Placed {len(parts)} footprints. Board is UNROUTED; do not fabricate.')
