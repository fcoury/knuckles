# Knuckles integrated controller — revision 0.2 engineering study

This revision integrates an nRF52840 radio module, USB-C, battery charging and
3.3 V regulation into dedicated left and right keyboard PCBs. It retains
27 keys per half and the right-hand TPS43. The default spacing is **18.5 mm**;
19.5 mm is generated from the same sources.

**These are engineering prototypes and have not been manufactured or tested.** The
firmware artifacts are experimental builds for the new circuit. Do not flash
them onto the working nice!nano keyboards or order these PCB files.

## Inspect the design

Open the routed boards in KiCad 8:

- [18.5 mm left routed](output/routed/18.5/left/knuckles_integrated_left.kicad_pro)
- [18.5 mm right routed](output/routed/18.5/right/knuckles_integrated_right.kicad_pro)
- [19.5 mm left routed](output/routed/19.5/left/knuckles_integrated_left.kicad_pro)
- [19.5 mm right routed](output/routed/19.5/right/knuckles_integrated_right.kicad_pro)

The complete schematic/generator projects remain separate:

- [18.5 mm left](output/integrated/18.5/knuckles_integrated_left.kicad_pro)
- [18.5 mm right](output/integrated/18.5/knuckles_integrated_right.kicad_pro)
- [19.5 mm left](output/integrated/19.5/knuckles_integrated_left.kicad_pro)
- [19.5 mm right](output/integrated/19.5/knuckles_integrated_right.kicad_pro)

These generator projects contain fixed power/USB/ground cells and open remaining
connections. The completed native layouts and their measured acceptance state are
separate under `output/routed/<spacing>/<hand>/summary.json`.

Each project includes the controller, power circuit and complete 27-key matrix
schematic. The native schematic references match the PCB. The separate
[45 × 55 mm controller study](output/knuckles_controller.kicad_pro) remains
available for electrical review; building a separate daughterboard is optional.

See [the engineering review and routing handoff](ENGINEERING.md),
[charging/bootloader build instructions](firmware/README.md),
[physical GPIO map](output/pin-map.json), and [component review BOM](output/bom-review.csv).
The BOM is for the controller study; it is **not** a keyboard manufacturing BOM.

## Decisions implemented

- Raytac MDBT50Q-1MV2 with calibrated internal low-frequency RC clock. The module
  provides the 32 MHz crystal, RF matching and antenna; there is no nice!nano.
- BQ25186 programmable charger and power path, followed by TPS63031 fixed 3.3 V
  buck-boost regulation. Independent PMIC and touchpad I2C buses.
- Protected 1S 4.2 V LiPo packs, from 110 through 500 mAh. The battery lives in
  the case, clear of the antenna; capacity alone does not specify dimensions.
- Charging profiles: 110 mAh / 20 mA; 250 mAh / 50 mA; 500 mAh / 100 mA.
  A different capacity requires a reviewed profile; the board cannot detect mAh.
- Charging is disabled in the default firmware **and** R12 is unpopulated.
  Enabling it requires the actual cell specification and a cell-mounted 10 kΩ,
  beta-3435 thermistor. J2 is battery power; J6 is the separate thermistor pair.
- Right half is the split central and USB/Bluetooth mouse/keyboard. Left sends
  its keys over BLE and uses a separate USB CDC function to negotiate charging.
- Four copper layers and a 1.6 mm board. Several small components and SWD pads
  are on the back, so assembly needs two sides. These placements remain subject
  to routing and case review.
- A case-mounted TPS43 holder replaces the two old controller cover holes.
  Its proposed position moves roughly 7 mm toward USB to clear the radio area.
  The five main case mounting holes remain.

## Rebuild and verify

From the repository root, with Node dependencies and Docker available:

```sh
npm run build:integrated
npm run build:integrated -- --spacing 19.5
npm run check:integrated
npm test
```

`build:integrated` starts from fresh Ergogen output and composes both halves.
It adds fixed local power and USB routes, without overwriting the normal PCB
outputs or generating Gerbers.
`check:integrated` exports ERC, DRC and netlists using pinned KiCad 8, compares
schematic nets with physical pads, and checks the matrix/power contracts.
It deliberately reports unconnected nets separately; passing is a placement
and electrical-consistency checkpoint, not fabrication clearance.

The retained [validation summary](output/validation-summary.json) records each
board's errors, warnings and unrouted connections. Retained routed warnings
include silkscreen/library details and dangling-track/via reports; these need
review before release, including ground-stitch intent after plane filling.

`circuit.py` is the controller electrical source. `integrate.py` contains the
initial placement and mechanical policy. `keyboard_schematic.py` adds the matrix
hierarchy. `generate.py` creates the controller sheets and custom lands.
`vendor-footprints.py` runs in the pinned KiCad image when adding standard lands.
`check-parts.py` refreshes catalog snapshots without buying or reserving parts.

Run the remaining outer-layer routing separately (both hands and spacings):

```sh
python3 hardware/integrated-controller/route-remaining.py --hand right --spacing 18.5
python3 hardware/integrated-controller/route-remaining.py --hand left --spacing 18.5
```

Repeat with `--spacing 19.5` for that geometry. `--fanout` enables the SMD
escape pre-pass; `--resume` continues a candidate. The pinned Freerouting JVM
writes disposable candidates under `output/candidates/<spacing>/<hand>/`.
A failed candidate remains available for inspection and exits nonzero.
Manual routing may still be required. These runs preserve the completed native
KiCad files under `output/routed/`, which are the authoritative finished layouts;
the generator rebuilds only the separate partial source projects.

Validate all four native layouts without rerouting:

```sh
npm run check:integrated:routed
```

This checks footprint positions/nets, protected routes, physical DRC, airwires,
USB ground coverage and via/paste intersections. Results are retained in
[the routed validation summary](output/routed/validation-summary.json).
The selected 3313 stack and calculator inputs are retained in
[stackup.json](references/stackup.json).

Export a completed native layout’s engineering-review files with:

```sh
python3 hardware/integrated-controller/export-review.py --hand right --spacing 18.5
```

This rechecks DRC, ground coverage and via/paste intersections before writing
Gerbers/drills, a controller-only BOM and a CPL draft under
`output/manufacturing-review/`. Rotations, stencil, sourcing, mechanics and bench
behavior still need review. The package is explicitly not approved for ordering.

## Remaining release gates

1. Secure the radio module. JLC's saved C5118826 listing has **zero stock**;
   consignment/global sourcing or a reviewed substitute still needs a quote.
2. Review the completed routing, ground planes, USB transitions, thermal vias
   and fabrication rules with the manufacturer. All four retained layouts pass
   zero-airwire/zero-physical-error checks; impedance and DFM remain review gates.
3. Confirm the touchpad, battery, connector/cable, switch and keycap clearances
   with a full-size print or mechanical prototype. Battery size is unresolved.
4. Bench-test supply startup/transients, idle/suspend current, SWD/UF2 recovery,
   both keyboard halves and TPS43, and charging/NTC behavior before fitting R12.
5. Complete manufacturing BOM/CPL, orientation review, module sourcing and USB
   product identification before release. No order or programming was performed.

## References and attribution

Manufacturer and upstream sources are recorded in [sources.json](sources.json).
Standard footprints are from KiCad 8 under
[CC BY-SA 4.0 with the KiCad library exception](https://www.kicad.org/libraries/license/).
The Alps SSSS811101 land derives from the repository's ceoloide footprint,
copyright Marco Massarelli 2023, with attribution to infused-kim and ceoloide,
under CC-BY-NC-SA-4.0. Its pad geometry was checked against Alps drawings.
The TI charger and ALPS reset lands follow the manufacturer drawings. Keyboard
switch, diode and artwork geometry retain the source repository's licenses.
