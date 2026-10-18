# Knuckles wireless PCB ordered on 2026-10-18

This directory preserves the exact saved autorouted PCB and Gerber ZIP used
for the JLCPCB order reported on 2026-10-18. Keep these files unchanged;
archive later orders in a new dated directory.

Upload `knuckles_wireless_autorouted.zip` to reproduce this manufacturing
revision. The board uses 18.5 mm key spacing, two copper layers, and a
1.6 mm board thickness. These are the design settings; the JLCPCB order
number and selected order options were not recorded here.

## Contents

- `knuckles_wireless_autorouted.kicad_pcb`: ordered board snapshot.
- `knuckles_wireless_autorouted.kicad_pro`: matching KiCad project rules.
- `knuckles_wireless_autorouted.zip`: exact manufacturing ZIP, including
  seven Gerber layers, plated and non-plated drills, and two drill maps.
- `build-info.json`: generated spacing selection.
- `drc.json`: independent pre-order check of the saved PCB using the
  repository's pinned KiCad 8.0.8 toolchain.
- `SHA256SUMS`: SHA-256 hashes of the archived artifacts and validation files.

## Pre-order verification

All 11 files in the ZIP matched a fresh KiBot export of the saved PCB using
`kibot/default.kibot.yaml`, apart from generation timestamps. The generated
and routed boards had matching pad properties, nets, and board outlines;
coordinate rounding was at most 0.000048 mm.

The independent DRC reported zero errors and zero unconnected items, with
193 warnings: 108 co-located holes with identical drill geometry, 65 missing
footprint-library warnings, and 20 silkscreen-clipping warnings. The export
subtracts solder-mask openings from silkscreen.

These checks establish manufacturing-file consistency and compliance with
the configured PCB rules. Electrical function and component fit require
hardware validation.

Verify the archive from this directory with `shasum -a 256 -c SHA256SUMS`.
