"""Electrical source for the Knuckles integrated-controller bring-up design.

Pin numbers are physical package/module pads, not Pro Micro pin numbers.
See README.md and sources.json for the references and release limitations.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PINS = json.loads((HERE/'references/module-pins.json').read_text())
PARTS = []

def add(ref, value, code, footprint, pins, nets, sheet, sch, pcb, *, dnp=False, note=''):
    PARTS.append(dict(ref=ref,value=value,lcsc=code,footprint=footprint,pins={str(k):v for k,v in pins.items()},nets={str(k):v for k,v in nets.items()},sheet=sheet,sch=sch,pcb=pcb,dnp=dnp,note=note))

def passive(ref,value,code,a,b,sheet,sch,pcb,dnp=False,note=''):
    kind='C' if ref.startswith('C') else 'R'
    fp='C_0603_1608Metric' if kind=='C' else 'R_0603_1608Metric'
    add(ref,value,code,fp,{'1':kind+'1','2':kind+'2'},{'1':a,'2':b},sheet,sch,pcb,dnp=dnp,note=note)

module_nets = {n:'GND' for n,v in MODULE_PINS.items() if v=='GND'}
module_nets.update({'28':'+3V3','30':'+3V3','32':'VBUS','34':'USB_MCU_DN','35':'USB_MCU_DP','40':'RESET_N','51':'SWDIO','53':'SWDCLK','41':'TPS_SDA','44':'TPS_SCL','20':'BATT_ADC','21':'BATT_SENSE_EN','22':'CHG_INT_N','23':'CHG_PG_N','24':'CHG_ALLOW','19':'PMIC_SDA','16':'PMIC_SCL'})
GPIO = {'R0':('P0.24','48'),'R1':('P1.00','47'),'R2':('P0.11','27'),'R3':('P1.04','56'),'R4':('P1.06','57'),'C0':('P0.31','12'),'C1':('P0.29','10'),'C2':('P0.02','11'),'C3':('P1.15','8'),'C4':('P1.13','6'),'C5':('P1.11','4')}
module_nets.update({pin:net for net,(gpio,pin) in GPIO.items()})
add('U1','MDBT50Q-1MV2','C5118826','Raytac_MDBT50Q',MODULE_PINS,module_nets,'core',[105,105],[22.5,8,0],note='Normal-voltage mode: VDD and VDDH tied to 3.3V; DCCH NC; LF clock uses calibrated internal RC. JLC stock zero at sourcing snapshot.')
usb_pins={k:k for k in ['A1','A4','A5','A6','A7','A8','A9','A12','B1','B4','B5','B6','B7','B8','B9','B12','S1']}
usb_nets={**dict.fromkeys(['A1','A12','B1','B12','S1'],'GND'),**dict.fromkeys(['A4','A9','B4','B9'],'VBUS'),'A5':'USB_CC1','B5':'USB_CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DN','B7':'USB_DN'}
add('J1','TYPE-C-31-M-12','C165948','USB_C_Receptacle_HRO_TYPE-C-31-M-12',usb_pins,usb_nets,'core',[215,55],[22.5,53,180])
add('U4','USBLC6-2SC6','C7519','SOT-23-6',{'1':'I/O1','2':'GND','3':'I/O2','4':'I/O2','5':'VBUS','6':'I/O1'},{'1':'USB_DP','6':'USB_DP','3':'USB_DN','4':'USB_DN','2':'GND','5':'VBUS'},'core',[215,135],[22.5,44,0])
for ref,net,pos in [('R1','USB_CC1',[215,95]),('R2','USB_CC2',[215,110])]:passive(ref,'5.1k','C23186',net,'GND','core',pos,[27+(ref=='R2')*3,48,90])
add('J2','S2B-PH-SM4-TB(LF)(SN)','C295747','JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal',{'1':'BAT+','2':'BAT-'},{'1':'VBAT','2':'GND'},'power',[40,45],[39,36,90],note='Protected 1S LiPo only. Verify actual cable polarity; capacity is not a voltage rating.')
add('J3','SM04B-SRSS-TB(LF)(SN)','C160404','JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',{'1':'3V3','2':'GND','3':'SDA','4':'SCL'},{'1':'+3V3','2':'GND','3':'TPS_SDA','4':'TPS_SCL'},'core',[310,190],[39.5,22,90],note='New custom cable to existing TPS43 adapter; connector is not the raw sensor FPC pinout.')
add('J4','Matrix bring-up header','', 'PinHeader_1x12_P2.54mm_Vertical',{str(n):name for n,name in enumerate(['GND']+list(GPIO),1)},{str(n):name for n,name in enumerate(['GND']+list(GPIO),1)},'core',[310,120],[3,15,0],dnp=True,note='Bench connector, manually fitted; replaced by matrix traces in keyboard integration.')
add('J5','SWD pogo interface','', 'SWD_2x3_P1.27_NoHoles',dict(zip(map(str,range(1,7)),['VTREF','SWDIO','GND','SWDCLK','RESET_N','GND'])),dict(zip(map(str,range(1,7)),['+3V3','SWDIO','GND','SWDCLK','RESET_N','GND'])),'core',[310,50],[37,10,0],dnp=True,note='Six bare pads on 1.27mm pitch; custom pogo fixture, not a mechanically compatible Tag-Connect connector. Pin 1 is target voltage sense, not external power input.')
add('SW1','SSSS811101','C109335','SSSS811101',{'1':'OFF','2':'COM','3':'ON'},{'1':'GND','2':'REG_EN','3':'SYS'},'power',[210,130],[43.5,46,0],note='ALPS SSSS811101; pad dimensions checked against manufacturer mounting drawing.')
add('SW2','SKRPANE010','C470426','SKRPANE010',{'1':'A1','2':'A2','3':'B1','4':'B2'},{'1':'RESET_N','2':'RESET_N','3':'GND','4':'GND'},'core',[55,205],[37,48,0])
passive('R3','10k','C25804','+3V3','RESET_N','core',[55,185],[36,44,0])
for ref,net,sch,pcb in [('R4','TPS_SDA',[270,220],[35,20,90]),('R5','TPS_SCL',[320,220],[35,24,90])]:passive(ref,'4.7k','C23162','+3V3',net,'core',sch,pcb,dnp=True,note='Fit only if the attached TPS43 adapter lacks pull-ups; confirm effective parallel pull-up resistance.')
for ref,net,sch,pcb in [('R6','CHG_INT_N',[45,245],[32,28,0]),('R7','CHG_PG_N',[105,245],[32,31,0])]:passive(ref,'10k','C25804','+3V3',net,'core',sch,pcb)
for ref,value,code,net,sch,pcb in [('C1','100nF','C14663','+3V3',[45,155],[15,16.5,0]),('C2','10uF','C19702','+3V3',[105,155],[19,16.5,0]),('C3','4.7uF','C19666','VBUS',[165,185],[26,44,90])]:passive(ref,value,code,net,'GND','core',sch,pcb)
add('U2','BQ25186DLHR','C44639442','TI_WSON_DLH0010A',dict(zip(map(str,range(1,12)),['SYS','BAT','PG_N','CE_N','GND','TS_MR','SDA','SCL','INT_N','IN','EP'])),{'1':'SYS','2':'VBAT','3':'CHG_PG_N','4':'CHG_EN_N','5':'GND','6':'BAT_NTC','7':'PMIC_SDA','8':'PMIC_SCL','9':'CHG_INT_N','10':'VBUS','11':'GND'},'power',[90,75],[32,36,0],note='I2C 0x6A on dedicated bus. CE held disabled until firmware verifies profile and USB state; R12 assembly interlock.')
add('U3','TPS63031DSKR','C15516','WSON-10-1EP_2.5x2.5mm_P0.5mm_EP1.2x2mm',dict(zip(map(str,range(1,12)),['VOUT','L2','PGND','L1','VIN','EN','PS_SYNC','VINA','GND','FB','EP'])),{'1':'+3V3','2':'SW_L2','3':'GND','4':'SW_L1','5':'SYS','6':'REG_EN','7':'GND','8':'SYS','9':'GND','10':'+3V3','11':'GND'},'power',[240,65],[20,27,0])
add('L1','1.5uH SWPA3015S1R5MT','C83434','L_Sunlord_SWPA3015S',{'1':'1','2':'2'},{'1':'SW_L1','2':'SW_L2'},'power',[240,35],[20,22.5,0],note='Procurement gate: catalog says 1R5MT, public Sunlord table specifies 1R5NT. Obtain exact MT current/tolerance specification before release.')
for ref,value,code,a,b,sch,pcb,dnp,note in [
('R8','10k','C25804','+3V3','PMIC_SDA',[45,125],[29,38,90],False,'Dedicated PMIC bus pull-up; independent of external TPS43 pull-ups.'),
('R9','10k','C25804','+3V3','PMIC_SCL',[90,125],[32,41,0],False,'Dedicated PMIC bus pull-up.'),
('R10','100k','C25803','CHG_ALLOW','GND',[145,125],[36,41,0],False,'Hardware defaults to disabled charging while MCU is off/reset.'),
('R11','100k','C25803','VBUS','CHG_EN_N',[40,170],[29,34,90],False,'VBUS-domain CE pull-up. Q3 isolates the MCU GPIO from 5V.'),
('R12','0R','C21189','CHG_EN_N','CHG_DRAIN',[100,170],[29,31,90],True,'Assembly charge interlock; fit after selected cell/NTC and firmware validation. Does not bypass firmware control.'),
('R13','1M','C22935','REG_EN','GND',[270,130],[25,27,90],False,'Keep the regulator disabled while the mechanical switch is between contacts.'),
]:passive(ref,value,code,a,b,'power',sch,pcb,dnp=dnp,note=note)
for ref,value,code,net,sch,pcb in [('C4','2.2uF','C23630','VBUS',[35,95],[32,33,0]),('C5','2.2uF','C23630','VBAT',[145,95],[36,36,90]),('C6','10uF','C19702','SYS',[145,60],[29,36,90]),('C8','10uF','C19702','SYS',[190,95],[16.5,27,90]),('C9','100nF','C14663','SYS',[240,95],[20,31,0]),('C10','10uF','C19702','+3V3',[295,55],[23.5,27,90]),('C11','10uF','C19702','+3V3',[295,85],[23.5,31,90])]:passive(ref,value,code,net,'GND','power',sch,pcb)
add('J6','External 10k NTC pads','', 'NTC_WirePads',{'1':'NTC','2':'GND'},{'1':'BAT_NTC','2':'GND'},'power',[40,210],[38,31,0],dnp=True,note='Attach an insulated external 10k NTC, beta 3435K, thermally coupled to the cell before enabling charging. Not simulated with a fixed resistor.')
# Battery sense is disconnected when the MCU is off or not sampling.
add('Q1','AO3401A','C15127','SOT-23',{'1':'G','2':'S','3':'D'},{'1':'BATT_GATE','2':'VBAT','3':'BATT_DIV_TOP'},'power',[210,190],[10,28,0])
add('Q2','2N7002','C8545','SOT-23',{'1':'G','2':'S','3':'D'},{'1':'BATT_SENSE_EN','2':'GND','3':'BATT_GATE'},'power',[210,225],[10,34,0])
for ref,a,b,sch,pcb in [('R14','VBAT','BATT_GATE',[160,190],[10,24,0]),('R15','BATT_DIV_TOP','BATT_ADC',[265,190],[14,29,0]),('R16','BATT_ADC','GND',[320,190],[14,32,0]),('R17','BATT_SENSE_EN','GND',[160,225],[10,38,0])]:passive(ref,'10k' if ref in ('R15','R16') else '1M','C25804' if ref in ('R15','R16') else 'C22935',a,b,'power',sch,pcb)
passive('C12','100nF','C14663','BATT_ADC','GND','power',[320,225],[14,35,0])
add('Q3','2N7002','C8545','SOT-23',{'1':'G','2':'S','3':'D'},{'1':'CHG_ALLOW','2':'GND','3':'CHG_DRAIN'},'power',[100,205],[27,40,0])
passive('R18','27R','C25190','USB_DP','USB_MCU_DP','core',[210,175],[26,16,90])
passive('R19','27R','C25190','USB_DN','USB_MCU_DN','core',[210,195],[29,16,90])
passive('C13','100nF','C14663','VBUS','GND','core',[165,225],[25.5,47,90])

# Keep the placement draft's power components and connector courtyards separate.
placements = {'J1':[22.5,52,0],'SW1':[41.5,46,0],'SW2':[35,48,0],
              'C2':[19,17.5,0],'C6':[28.5,35,90],'R11':[26.3,34,90],'R13':[27,27,90],
              'R8':[29,39,0],'R9':[30,42,0],'R10':[32,44,0],
              'J2':[39,34,90],'C5':[32,39,90],'J6':[38,53,0],
              'U4':[22.5,43.5,0],'C3':[31.5,16.5,90],'R1':[15,47,90],'R2':[15,51,90],
              'Q3':[25,39,0],'R18':[26,18.5,90],'R19':[29,18.5,90],'C13':[26,43.5,90]}
for part in PARTS:
    if part['ref'] in placements: part['pcb']=placements[part['ref']]

# Preserve capacitance under DC bias. Samsung typical curves give ~11.77uF
# at 4.5V and ~14.90uF at 3.3V for this 22uF/25V 0805 part; see audit.
for part in PARTS:
    if part['ref'] in {'C2','C6','C8','C10','C11'}:
        part.update(value='22uF',lcsc='C45783',footprint='C_0805_2012Metric')
