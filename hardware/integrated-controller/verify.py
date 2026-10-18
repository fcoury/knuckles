"""Independent electrical contracts, run in pinned KiCad 8 after CLI exports."""
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as pcb
from circuit import PARTS, HERE

# Reviewed physical pads, deliberately independent of circuit.py's GPIO table.
MATRIX={'R0':'48','R1':'47','R2':'27','R3':'56','R4':'57',
        'C0':'12','C1':'10','C2':'11','C3':'8','C4':'6','C5':'4'}
PMIC={'1':'SYS','2':'VBAT','3':'CHG_PG_N','4':'CHG_EN_N','5':'GND',
      '6':'BAT_NTC','7':'PMIC_SDA','8':'PMIC_SCL','9':'CHG_INT_N','10':'VBUS','11':'GND'}

def check(board_path):
    b=pcb.LoadBoard(str(board_path))
    def pads(ref):
        f=b.FindFootprintByReference(ref);assert f,ref
        return {p.GetNumber():p.GetNetname() for p in f.Pads() if p.GetNumber()}
    left='integrated_left' in board_path.name
    for part in PARTS:
        fp=b.FindFootprintByReference(part['ref'])
        if fp:
            assert fp.GetValue()==part['value'],part['ref']
            for pin,net in part['nets'].items():
                if left and part['ref']=='U1' and pin in ['41','44']: continue
                assert pads(part['ref'])[pin]==net
    module=pads('U1')
    for net,pin in MATRIX.items(): assert module[pin]==net,(pin,net)
    assert pads('U2')==PMIC
    for pin,net in {'28':'+3V3','30':'+3V3','32':'VBUS','34':'USB_MCU_DN',
                    '35':'USB_MCU_DP','19':'PMIC_SDA','16':'PMIC_SCL','24':'CHG_ALLOW',
                    '20':'BATT_ADC','21':'BATT_SENSE_EN','41':'TPS_SDA','44':'TPS_SCL'}.items():
        assert module[pin]==('' if left and pin in ['41','44'] else net),(pin,net)
    assert not module['31'] # DCCH is unused in normal voltage mode.
    assert pads('R18')=={'1':'USB_DP','2':'USB_MCU_DP'}
    assert pads('R19')=={'1':'USB_DN','2':'USB_MCU_DN'}
    assert pads('R11')=={'1':'VBUS','2':'CHG_EN_N'}
    assert pads('R12')=={'1':'CHG_EN_N','2':'CHG_DRAIN'}
    assert pads('Q3')=={'1':'CHG_ALLOW','2':'GND','3':'CHG_DRAIN'}
    assert b.FindFootprintByReference('R12').GetAttributes() & pcb.FP_EXCLUDE_FROM_BOM
    assert pads('SW1')=={'1':'GND','2':'REG_EN','3':'SYS'}
    # Compare the exported Eeschema netlist with every electrically connected pad.
    netlist=ET.parse(board_path.with_suffix('.net.xml'))
    schematic={(n.attrib['ref'],n.attrib['pin']):net.attrib['name']
               for net in netlist.findall('./nets/net') for n in net.findall('node')
               if not net.attrib['name'].startswith('unconnected-') and not n.attrib['ref'].startswith('#')}
    actual={(f.GetReference(),p.GetNumber()):p.GetNetname() for f in b.GetFootprints()
            for p in f.Pads() if p.GetNetname()}
    assert actual==schematic,{'PCB_only':set(actual.items())-set(schematic.items()),
                             'schematic_only':set(schematic.items())-set(actual.items())}
    if 'integrated_' in board_path.name:
        assert b.GetCopperLayerCount()==4
        assert b.GetEnabledLayers().Contains(pcb.In1_Cu) and b.GetEnabledLayers().Contains(pcb.In2_Cu)
        cells=set()
        for n in range(28,55):
            sw=pads('S'+str(n));diode=pads('D'+str(n))
            assert sw['2']==diode['2'] and sw['1'].startswith('C') and diode['1'].startswith('R')
            cell=(int(diode['1'][1:]),int(sw['1'][1:]));assert cell not in cells;cells.add(cell)
        assert cells=={(r,c) for r in range(4) for c in range(6)}|{(4,3),(4,4),(4,5)}
        assert not b.FindFootprintByReference('J4')
        assert bool(b.FindFootprintByReference('J3'))==('right' in board_path.name)
    print(board_path.name+': schematic/pads, power and 27-key matrix contracts passed')

if __name__=='__main__':
    parts={p['ref']:p for p in PARTS}
    assert parts['R15']['value']==parts['R16']['value']=='10k'
    assert parts['C12']['value']=='100nF'
    tau=(10000/2)*100e-9
    assert math.exp(-.010/tau)<1e-6 # Existing ZMK 10ms measurement delay.
    for ref in ['C2','C6','C8','C10','C11']:
        assert parts[ref]['lcsc']=='C45783' and parts[ref]['footprint']=='C_0805_2012Metric'
    for path in [HERE/'output/knuckles_controller.kicad_pcb',*sorted((HERE/'output/integrated').glob('*/*.kicad_pcb'))]:check(path)
