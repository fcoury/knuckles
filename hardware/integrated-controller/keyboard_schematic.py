"""Generate the complete per-half electrical hierarchy from composed pads.

Placement/row-column contracts are checked separately in verify.py. Symbols
are embedded; matrix references deliberately match the Ergogen PCB references.
"""
from copy import deepcopy
import generate as g

def write(out, project, board, controller):
    parts=deepcopy(controller)
    for fp in board.GetFootprints():
        ref=fp.GetReference()
        if not (ref[0] in 'SD' and ref[1:].isdigit()): continue
        key_index=int(ref[1:])-28
        page=key_index//9
        x=60+(key_index%3)*120
        y=50+((key_index%9)//3)*75+(25 if ref.startswith('D') else 0)
        nets={p.GetNumber():p.GetNetname() for p in fp.Pads() if p.GetNetname()}
        parts.append(dict(ref=ref,value='Schottky diode; K to row' if ref.startswith('D') else 'Choc switch',
                          lcsc='',footprint=str(fp.GetFPID().GetLibItemName()),
                          pins={'1':'K','2':'A'} if ref.startswith('D') else {'1':'Column','2':'Diode','3':'NC'},
                          nets=nets,sheet=f'matrix{page+1}',sch=[x,y],dnp=False))
    symbols=''.join(g.symbol(p).replace('"Knuckles:'+p['ref']+'"','"'+p['ref']+'"',1)
                    for p in g.PARTS+[p for p in parts if p['sheet'].startswith('matrix')])
    symbols+=g.FLAG.replace('"Knuckles:PWR_FLAG"','"PWR_FLAG"',1)
    (g.HERE/'libraries/KnucklesKeyboard.kicad_sym').write_text(
        '(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+symbols+')\n')
    (out/'sym-lib-table').write_text('(sym_lib_table (lib (name "Knuckles") (type "KiCad") (uri "${KIPRJMOD}/../../../libraries/KnucklesKeyboard.kicad_sym") (options "") (descr "Integrated keyboard symbols")))\n')
    root_id=g.uid(project+'-root')
    names=['core','power','matrix1','matrix2','matrix3']
    root=f'(kicad_sch (version 20231120) (generator eeschema) (uuid {root_id}) (paper "A3") (title_block (title {g.q(project)}) (rev "0.2 REVIEW")) (lib_symbols)'
    for i,name in enumerate(names):
        sid=g.uid(project+'-'+name);filename=f'{project}-{name}.kicad_sch'
        (out/filename).write_text(g.sheet(name,parts,project,root_id,sid))
        x=30+(i%3)*125;y=65+(i//3)*90
        root+=f'(sheet (at {x} {y}) (size 95 45) (stroke (width .1524) (type default)) (fill (color 0 0 0 0)) (uuid {sid}) {g.prop("Sheetname",name,x,y-2)} {g.prop("Sheetfile",filename,x,y+47)} (instances (project {g.q(project)} (path {g.q("/"+root_id)} (page {g.q(str(i+2))})))))'
    root+=f'(text "UNROUTED ENGINEERING STUDY — NOT FOR FABRICATION" (at 30 25 0) (effects (font (size 2 2)) (justify left)) (uuid {g.uid(project+"-notice")}))'
    (out/(project+'.kicad_sch')).write_text(root+')\n')
    # Keep PCB instance paths aligned for later schematic-to-PCB updates.
    import pcbnew as pcb
    for part in parts:
        fp=board.FindFootprintByReference(part['ref'])
        fp.SetPath(pcb.KIID_PATH('/'+root_id+'/'+g.uid(project+'-'+part['sheet'])+'/'+g.uid(part['ref'])))
