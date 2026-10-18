"""Run inside the pinned KiCad 8 image to vendor standard footprints."""
import shutil
from pathlib import Path
from circuit import PARTS, HERE
base=Path('/usr/share/kicad/footprints')
out=HERE/'libraries/Knuckles.pretty'
out.mkdir(parents=True,exist_ok=True)
custom={'TI_WSON_DLH0010A','SSSS811101','SKRPANE010','NTC_WirePads','SWD_2x3_P1.27_NoHoles'}
for name in sorted({p['footprint'] for p in PARTS}-custom):
    matches=list(base.glob('*.pretty/'+name+'.kicad_mod'))
    if len(matches)!=1:raise RuntimeError(f'Expected exactly one KiCad 8 footprint: {name}, found {matches}')
    shutil.copy(matches[0],out/matches[0].name)
