#!/usr/bin/env python3
"""Generate the review schematics, circuit manifest, BOM, and custom footprints.

Uses only the Python standard library. PCB placement is handled separately by
place-board.py in the pinned KiCad 8 container; this script never orders parts.
"""
import csv
import json
import math
import uuid
from pathlib import Path
from circuit import PARTS, GPIO, HERE

OUT=HERE/'output'
OUT.mkdir(exist_ok=True)
LIB=HERE/'libraries/Knuckles.pretty'
LIB.mkdir(exist_ok=True)
q=lambda x:json.dumps(str(x),ensure_ascii=False)
uid=lambda name:str(uuid.uuid5(uuid.NAMESPACE_URL,'https://github.com/fcoury/knuckles/integrated-controller/'+name))
ROOT_ID=uid('root')
PROJECT='knuckles_controller'
FONT='(effects (font (size 1 1)))'


def prop(name,value,x,y,hide=False):
    return f'(property {q(name)} {q(value)} (at {x} {y} 0) (effects (font (size 1 1)) {"hide" if hide else ""}))'


def pin_layout(part):
    pins=list(part['pins'].items())
    if part['ref']=='U1': pins.sort(key=lambda pair:int(pair[0]))
    if part['ref'][0] in 'RC' and len(pins)==2:
        return [(pins[0][0],pins[0][1],-5.08,0,0),(pins[1][0],pins[1][1],5.08,0,180)],2.54,2.54
    count=(len(pins)+1)//2
    height=max(5.08,(count+1)*2.54/2)
    result=[]
    for n,(number,name) in enumerate(pins):
        side=-1 if n<count else 1
        row=n if n<count else n-count
        y=(count-1)*1.27-row*2.54
        result.append((number,name,side*17.78,y,0 if side<0 else 180))
    return result,15.24,height


def pin_type(part,num):
    if part['ref']=='U1':
        name=part['pins'][num]
        return 'power_in' if name in ('GND','VDD','VDDH','VBUS') else 'bidirectional'
    if part['ref']=='U2':
        if num=='1':return 'power_out'
        if num in ('2','5','10','11'):return 'power_in'
        if num in ('3','9'):return 'open_collector'
        return 'bidirectional' if num in ('7','8') else 'input'
    if part['ref']=='U3':
        if num=='1':return 'power_out'
        if num in ('3','5','8','9','11'):return 'power_in'
        return 'passive' if num in ('2','4') else 'input'
    return 'passive'


def symbol(part):
    pins,w,h=pin_layout(part)
    name='Knuckles:'+part['ref']
    shapes=f'(rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background)))'
    if part['ref'].startswith('C'):
        shapes='(polyline (pts (xy -0.6 -2.54)(xy -0.6 2.54)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.6 -2.54)(xy 0.6 2.54)) (stroke (width 0.254) (type default)) (fill (type none)))'
        shapes+='(polyline (pts (xy -2.54 0)(xy -0.6 0)) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy 0.6 0)(xy 2.54 0)) (stroke (width 0.254) (type default)) (fill (type none)))'
    body=f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes) {prop("Reference",part["ref"],0,h+3.81)} {prop("Value",part["value"],0,h+1.27)} (symbol {q(part["ref"]+"_0_1")} {shapes}) (symbol {q(part["ref"]+"_1_1")} '
    for num,label,x,y,angle in pins:
        body+=f'(pin {pin_type(part,num)} line (at {x} {y} {angle}) (length 2.54) (name {q(label)} (effects (font (size 0.85 0.85)))) (number {q(num)} (effects (font (size 0.85 0.85)))))'
    return body+'))'


FLAG = '(symbol "Knuckles:PWR_FLAG" (power) (pin_numbers hide) (pin_names (offset 0) hide) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 2 0) (effects (font (size 1 1)) hide)) (property "Value" "PWR_FLAG" (at 0 4 0) (effects (font (size 1 1)))) (symbol "PWR_FLAG_0_1" (polyline (pts (xy 0 0)(xy 0 1.27)(xy -1.27 1.27)(xy 0 2.54)(xy 1.27 1.27)(xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))) (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'


def sheet(name, parts=PARTS, project=PROJECT, root_id=ROOT_ID, sheet_id=None):
    selected=[p for p in parts if p['sheet']==name]
    sid=sheet_id or uid('sheet-'+name)
    text=f'(kicad_sch (version 20231120) (generator eeschema) (uuid {sid}) (paper "A3") (title_block (title {q("Knuckles integrated controller — "+name)}) (rev "0.2 REVIEW") (company "Knuckles")) (lib_symbols '+''.join(symbol(p) for p in selected)+FLAG+')'
    text+=f'(text "REVIEW DESIGN — NOT RELEASED FOR FABRICATION" (at 20 20 0) (effects (font (size 2 2)) (justify left)) (uuid {uid(name+"-notice")}))'
    for part in selected:
        x,y=[round(round(v/1.27)*1.27,4) for v in part['sch']];pins,w,h=pin_layout(part);ref=part['ref'];part_id=uid(ref)
        text+=f'(symbol (lib_id {q("Knuckles:"+ref)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if part["dnp"] else "no"}) (uuid {part_id})'
        text+=prop('Reference',ref,x,y-h-4)+prop('Value',part['value'],x,y-h-2)
        text+=prop('Footprint','Knuckles:'+part['footprint'],x,y,True)+prop('LCSC',part['lcsc'],x,y,True)
        for num,*_ in pins:text+=f'(pin {q(num)} (uuid {uid(ref+"-pin-"+num)}))'
        text+=f'(instances (project {q(project)} (path {q("/"+root_id+"/"+sid)} (reference {q(ref)}) (unit 1)))))'
        for num,label,px,py,angle in pins:
            sx=round(x+px,4);sy=round(y-py,4)
            net=part['nets'].get(num)
            if net:
                ex=round(sx+(-5.08 if px<0 else 5.08),4)
                text+=f'(wire (pts (xy {sx} {sy})(xy {ex} {sy})) (stroke (width 0) (type default)) (uuid {uid(ref+num+"wire")}))'
                # Global labels join the core and power sheets by net name.
                orient=0 if px<0 else 180
                justify='left' if px<0 else 'right'
                text+=f'(global_label {q(net)} (shape bidirectional) (at {ex} {sy} {orient}) (effects (font (size 0.85 0.85)) (justify {justify})) (uuid {uid(ref+num+"label")}))'
            else:text+=f'(no_connect (at {sx} {sy}) (uuid {uid(ref+num+"nc")}))'
    # Explicit external supplies; SYS and +3V3 are driven by their regulator symbols.
    if name=='power':
        for i,net in enumerate(['GND','VBAT','VBUS']):
            x=round(round((35+i*60)/1.27)*1.27,4);y=round(round(265/1.27)*1.27,4)
            ref='#FLG0'+str(i+1)
            text+=f'(symbol (lib_id "Knuckles:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid {uid(ref)}) {prop("Reference",ref,x,y,True)} {prop("Value","PWR_FLAG",x,y-4)} (pin "1" (uuid {uid(ref+"pin")})) (instances (project {q(project)} (path {q("/"+root_id+"/"+sid)} (reference {q(ref)}) (unit 1)))))'
            text+=f'(global_label {q(net)} (shape bidirectional) (at {x} {y} 0) (effects (font (size 1 1)) (justify left)) (uuid {uid(ref+"label")}))'
    return text+')\n'


def pad(num,x,y,w,h,layers='"F.Cu" "F.Paste" "F.Mask"'):
    return f'(pad {q(num)} smd roundrect (at {x} {y}) (size {w} {h}) (layers {layers}) (roundrect_rratio 0.2))'


def footprint(name,body,w,h):
    return f'(footprint {q(name)} (version 20240108) (generator pcbnew) (layer "F.Cu") (attr smd) (property "Reference" "REF**" (at 0 {-h/2-1} 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12)))) (property "Value" {q(name)} (at 0 {h/2+1} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12)))) (fp_rect (start {-w/2} {-h/2}) (end {w/2} {h/2}) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab")) (fp_rect (start {-w/2-.25} {-h/2-.25}) (end {w/2+.25} {h/2+.25}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd")) {body})\n'


def custom_footprints():
    # TI DLH0010A land-pattern dimensions, datasheet p30: 0.4 pitch,
    # 2.1 row spacing, 0.5x0.2 lands, 0.9x1.5 exposed GND pad.
    body=''
    for n in range(1,6):body+=pad(str(n),-1.05,round((n-3)*.4,3),.5,.2)
    for n in range(6,11):body+=pad(str(n),1.05,round((8-n)*.4,3),.5,.2)
    body+=pad('11',0,0,.9,1.5,'"F.Cu" "F.Mask"')
    body+=pad('',0,0,.75,1.15,'"F.Paste"')
    (LIB/'TI_WSON_DLH0010A.kicad_mod').write_text(footprint('TI_WSON_DLH0010A',body,2.6,2.2))
    # ALPS mounting-face land drawing: X gap 3.1/overall 5.2;
    # Y gap 1.5/overall 2.8. Circuit 1-2 and 3-4 are internally paired.
    body=''
    for num,x,y in [('1',-2.075,-1.075),('2',2.075,-1.075),('3',-2.075,1.075),('4',2.075,1.075)]:body+=pad(num,x,y,1.05,.65)
    (LIB/'SKRPANE010.kicad_mod').write_text(footprint('SKRPANE010',body,5.2,3.2))
    # Derived from ceoloide/power_switch_smd_side.js (Alps
    # SSSS811101), CC-BY-NC-SA-4.0, Marco Massarelli 2023; infused-kim/ceoloide.
    # Dimensions and common terminal 2 checked against the ALPS SSSS8 drawing.
    body=''
    for n,y in [('1',2.25),('2',-.75),('3',-2.25)]:body+=pad(n,-1.735,y,1.5,.7)
    for x in [-1.085,1.125]:
        for y in [-3.65,3.65]:body+=pad('',x,y,.8,1)
    for y in [-1.5,1.5]:body+=f'(pad "" np_thru_hole circle (at .025 {y}) (size .9 .9) (drill .9) (layers "*.Cu" "*.Mask"))'
    (LIB/'SSSS811101.kicad_mod').write_text(footprint('SSSS811101',body,6.2,8.8))
    (LIB/'NTC_WirePads.kicad_mod').write_text(footprint('NTC_WirePads',pad('1',-1.5,0,1.5,2)+pad('2',1.5,0,1.5,2),5,3))
    body=''.join(pad(str(1+2*row+col),(col-.5)*1.27,(row-1)*1.27,.9,.9,'"F.Cu" "F.Mask"') for row in range(3) for col in range(2))
    (LIB/'SWD_2x3_P1.27_NoHoles.kicad_mod').write_text(footprint('SWD_2x3_P1.27_NoHoles',body,2.2,3.5))


def main():
    custom_footprints()
    symbols=''.join(symbol(p).replace('"Knuckles:'+p['ref']+'"','"'+p['ref']+'"',1) for p in PARTS)
    symbols+=FLAG.replace('"Knuckles:PWR_FLAG"','"PWR_FLAG"',1)
    (HERE/'libraries/Knuckles.kicad_sym').write_text('(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor) '+symbols+')\n')
    (OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Knuckles") (type "KiCad") (uri "${KIPRJMOD}/../libraries/Knuckles.kicad_sym") (options "") (descr "Integrated controller review symbols")))\n')
    (OUT/'circuit.json').write_text(json.dumps(PARTS,indent=2)+'\n')
    for name in ['core','power']:(OUT/(name+'.kicad_sch')).write_text(sheet(name))
    root=f'(kicad_sch (version 20231120) (generator eeschema) (uuid {ROOT_ID}) (paper "A4") (title_block (title "Knuckles integrated nRF52840 controller") (rev "0.2 REVIEW")) (lib_symbols)'
    for i,name in enumerate(['core','power']):
        x=40+i*125;y=65;sid=uid('sheet-'+name)
        root+=f'(sheet (at {x} {y}) (size 80 45) (fields_autoplaced) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid {sid}) {prop("Sheetname",name,x,y-2)} {prop("Sheetfile",name+".kicad_sch",x,y+47)} (instances (project {q(PROJECT)} (path {q("/"+ROOT_ID)} (page {q(str(i+2))})))))'
    for y,line in [(30,'Knuckles integrated controller — engineering review'),(130,'1S 4.2V LiPo • 110–500mAh with matching firmware battery profile'),(140,'BQ25186: programmable current / 12-hour timer / USB suspend'),(150,'CHARGING DISABLED: R12 interlock + firmware control; verify cell/NTC'),(160,'Prototype circuitry; not a fabrication release')]:root+=f'(text {q(line)} (at 30 {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(line)}))'
    (OUT/(PROJECT+'.kicad_sch')).write_text(root+')\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Knuckles") (type "KiCad") (uri "${KIPRJMOD}/../libraries/Knuckles.pretty") (options "") (descr "Vendored KiCad 8 plus reviewed custom lands")))\n')
    (OUT/'knuckles_controller.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_copper_edge_clearance':.25}}},'meta':{'filename':'knuckles_controller.kicad_pro','version':1}},indent=2)+'\n')
    snapshot={r.get('componentCode'):r for r in json.loads((HERE/'parts-snapshot.json').read_text())}
    with (OUT/'bom-review.csv').open('w',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['Designator','Value','Footprint','LCSC Part #','Populate','Catalog MPN','Catalog stock snapshot','Notes'])
        for p in PARTS:
            stock=snapshot.get(p['lcsc'],{})
            w.writerow([p['ref'],p['value'],p['footprint'],p['lcsc'],'DNP' if p['dnp'] else 'yes',stock.get('componentModelEn',''),stock.get('overseasStockCount','unknown'),p['note']])
    (OUT/'pin-map.json').write_text(json.dumps({'matrix':{net:{'gpio':gpio,'module_pad':pin} for net,(gpio,pin) in GPIO.items()},'touchpad':{'SDA':'P0.17','SCL':'P0.20'},'battery':{'adc':'P0.04/AIN2','enable':'P0.05'},'charger':{'SDA':'P0.26','SCL':'P0.27','enable':'P0.08','interrupt':'P0.06','power_good':'P0.07','address':'0x6a'},'reset':'P0.18','lf_clock':'internal RC, calibrate'},indent=2)+'\n')
    print(f'Generated {len(PARTS)} components, 3 schematic sheets, BOM, and pad/GPIO map in {OUT}')

if __name__=='__main__':main()
