#!/usr/bin/env python3
"""Build the integrated board only. Never flashes a device or alters nice!nano builds."""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
IMAGE='zmkfirmware/zmk-build-arm@sha256:edb1c953438c6f720ddb79c3762f3972013b7fbbaf4fff3592fc869983e7afc5'
REVISIONS={'zmk':'edf5c0814fd3ea202e43aad2d68fd32e882a518c',
           'zephyr':'dacab4875df72109b96cc8977547a0dc04875bcd',
           'zmk-driver-azoteq-iqs5xx':'e19e55deaf8eeb0d32d9c2fe17e3f87f5287a5a5'}
BOOT='eefbe6bda98b80cb296e2f1bb1c982d58fe4c12d'
def run(args,cwd=None):subprocess.run(args,cwd=cwd,check=True)
def output(args,cwd=None):return subprocess.check_output(args,cwd=cwd,text=True).strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser()
parser.add_argument('--workspace',type=Path,required=True,help='Prepared west workspace; see README')
parser.add_argument('--bootloader',type=Path,required=True,help='Adafruit 0.9.2 checkout with submodules')
args=parser.parse_args();work=args.workspace.resolve();boot=args.bootloader.resolve()
for project,revision in REVISIONS.items():
    assert output(['git','rev-parse','HEAD'],work/project)==revision,project+' revision mismatch'
    if project!='zmk-driver-azoteq-iqs5xx':
        assert not output(['git','diff','HEAD','--'],work/project),project+' has tracked changes'
driver=work/'zmk-driver-azoteq-iqs5xx'
patch=HERE/'patches/iqs5xx-poll-wake.patch'
actual=output(['git','diff','HEAD','--src-prefix=a/','--dst-prefix=b/','--'],driver)
if not actual:run(['git','apply',str(patch)],driver)
else:assert actual==patch.read_text().strip(),'Unexpected touchpad driver modifications'
assert output(['git','rev-parse','HEAD'],boot)==BOOT,'Bootloader revision mismatch'
assert not output(['git','diff','HEAD','--'],boot),'Bootloader has tracked changes'
artifacts=HERE/'artifacts';artifacts.mkdir(exist_ok=True)
manifest={'experimental':True,'hardware_tested':False,'charging_enabled':False,'toolchain_image':IMAGE,
          'compiled_gpio_contracts':True,'source_revisions':REVISIONS,'bootloader_revision':BOOT,'artifacts':{}}
for hand in ['left','right']:
    conf='left-usb.conf' if hand=='left' else 'right-power.conf'
    run(['docker','run','--rm','-v',f'{work}:/work','-v',f'{HERE}:/design','-w','/work',IMAGE,
         'west','build','-p','always','-s','zmk/app','-d',f'build/knuckles-integrated-{hand}',
         '-b','knuckles_integrated','--','-DZephyr_DIR=/work/zephyr/share/zephyr-package/cmake',
         '-DZMK_CONFIG=/design/config','-DBOARD_ROOT=/design','-DZMK_EXTRA_MODULES=/design',
         f'-DSHIELD=knuckles_tps43_{hand}',f'-DEXTRA_CONF_FILE=/design/{conf}'])
    build=work/f'build/knuckles-integrated-{hand}/zephyr'
    config=(build/'.config').read_text()
    for required in ['CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC=y','CONFIG_CLOCK_CONTROL_NRF_K32SRC_RC_CALIBRATION=y',
                     'CONFIG_SOC_DCDC_NRF52X=y','CONFIG_USB_MAX_POWER=125',
                     '# CONFIG_KNUCKLES_BATTERY_VERIFIED is not set','# CONFIG_ZMK_SLEEP is not set']:
        assert required in config,required
    assert 'CONFIG_SOC_DCDC_NRF52X_HV=y' not in config
    assert ('CONFIG_ZMK_SPLIT_ROLE_CENTRAL=y' in config)==(hand=='right')
    assert ('CONFIG_INPUT_AZOTEQ_IQS5XX=y' in config)==(hand=='right')
    if hand=='left':assert 'CONFIG_USB_CDC_ACM=y' in config
    dts=(build/'zephyr.dts').read_text()
    def gpio_contract(prop, expected):
        value=re.search(r'\b'+re.escape(prop)+r'\s*=([^;]+);',dts).group(1)
        actual=[(int(port),int(pin,16)) for port,pin in re.findall(r'&gpio(\d+)\s+0x([0-9a-f]+)',value)]
        assert actual==expected,(hand,prop,actual)
    gpio_contract('row-gpios',[(0,24),(1,0),(0,11),(1,4),(1,6)])
    columns=[(0,31),(0,29),(0,2),(1,15),(1,13),(1,11)]
    gpio_contract('col-gpios',columns if hand=='left' else columns[::-1])
    gpio_contract('enable-gpios',[(0,8)])
    gpio_contract('interrupt-gpios',[(0,6)])
    gpio_contract('power-gpios',[(0,5)])
    for block, pins in [('pmic_default',[0xc001a,0xb001b]),('tps_default',[0xc0011,0xb0014])]:
        text=dts[dts.index(block+':'):];text=text[:text.index('};')]
        psels=re.search(r'psels\s*=([^;]+);',text).group(1)
        assert [int(x,16) for x in re.findall(r'0x([0-9a-f]+)',psels)]==pins
    assert re.search(r'io-channels\s*=\s*< &adc 0x2 >',dts)
    name=f'knuckles-integrated-{hand}.uf2';target=artifacts/name
    shutil.copy(build/'zmk.uf2',target)
    data=target.read_bytes();addresses=[]
    for off in range(0,len(data),512):
        a,b,flags,address,size,block,total,family=struct.unpack_from('<8I',data,off)
        assert (a,b,family)==(0x0a324655,0x9e5d5157,0xada52840)
        assert 0x26000<=address and address+size<=0xec000
        addresses.append(address)
    assert min(addresses)==0x26000
    manifest['artifacts'][name]={'sha256':digest(target),'bytes':len(data),'start_address':'0x26000'}
shutil.copytree(HERE/'bootloader/knuckles_integrated',boot/'src/boards/knuckles_integrated',dirs_exist_ok=True)
hexname='knuckles_integrated_bootloader-0.9.2_s140_6.1.1.hex'
run(['docker','run','--rm','-v',f'{boot}:/boot','-w','/boot',IMAGE,'make','-j4',
     'BOARD=knuckles_integrated','CROSS_COMPILE=/opt/zephyr-sdk-0.16.9/arm-zephyr-eabi/bin/arm-zephyr-eabi-',
     '_build/build-knuckles_integrated/'+hexname])
target=artifacts/hexname;shutil.copy(boot/'_build/build-knuckles_integrated'/hexname,target)
manifest['artifacts'][hexname]={'sha256':digest(target),'bytes':target.stat().st_size}
# Retain reproducibility evidence without committing generated binaries.
(HERE/'build-verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Experimental artifacts built and checked; no device flashed. '+str(artifacts))
