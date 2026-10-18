# Integrated controller engineering draft

This branch explores replacing each nice!nano with an on-board nRF52840
controller. The files here describe a separate 45 × 55 mm controller bring-up
board, **not a completed keyboard PCB or a fabrication release**.

Open `output/knuckles_controller.kicad_pro` in KiCad 8 to inspect the three-sheet
schematic and unrouted placement draft. `circuit.py` is the electrical source;
`output/bom-review.csv` includes assembly options and sourcing notes.

## Proposed circuit

- Raytac MDBT50Q-1MV2 module, USB-C with ESD protection, and SWD programming pads.
- BQ25185 charger with power path and TPS63031 3.3 V buck-boost regulator.
- Protected single-cell 3.7 V LiPo, charged to 4.2 V. Larger capacities use the
  same connector and voltage; verify cable polarity and provide case space.
- Default 20 mA charge setting for the 110 mAh baseline. Charging is disabled
  by leaving R12 unpopulated until the cell rating and external 10 kΩ,
  beta-3435 K thermistor are verified. Larger batteries need a reviewed charging
  profile, including the safety timer; a resistor change can increase current,
  subject to the present 100 mA input limit and system consumption.
- Matrix GPIO assignments follow the working controller mapping. A new four-pin
  TPS43 adapter cable carries 3.3 V, GND, SDA and SCL; retain polling firmware.
- Firmware and bootloader must use the calibrated internal low-frequency RC
  clock. No bootloader or firmware has been built or tested for this circuit.

## Validation and remaining work

The checked-in KiCad 8 ERC report contains zero violations. This checks the
schematic's electrical rules, not circuit correctness or hardware operation.
The placement DRC report contains physical errors and unconnected nets.

Before routing or ordering:

1. Resolve SW1: its provisional MSK12C02 assignment currently uses geometry
   derived from an Alps SSSS811101 footprint. The part and land pattern must
   be matched; the current pairing must not be fabricated.
2. Correct connector orientation, overlaps, copper-edge clearances and
   silkscreen, then review regulator loops, USB routing and antenna clearance.
3. Secure module sourcing. The saved JLC catalog snapshot reports zero stock
   for C5118826; catalog listings are not an assembly reservation or quote.
4. Review charger settings, thermistor behavior, battery protection and all
   package pinouts against manufacturer documentation.
5. Route and validate the controller, build its firmware, and test a prototype
   before integrating it into the 18.5 mm keyboard PCB. Prepare manufacturing
   BOM/CPL and programming instructions only after that review.

## Regeneration

Run `python3 -B hardware/integrated-controller/generate.py` from the repository
root to regenerate schematic sheets, custom footprints, BOM and pin map.
`vendor-footprints.py` and `place-board.py` run with KiCad 8's Python environment.
The reference environment is:

```
ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65
```

For example, mount this directory at `/work`, use `/work` as the working
directory, and run `python3 place-board.py`. Re-export ERC and DRC reports after
changing the design. `check-parts.py` refreshes public catalog data; it does not
purchase or reserve components.

## References and footprint attribution

Primary circuit references are listed in `sources.json`. Vendored standard
footprints come from the KiCad 8 libraries, under their
[CC BY-SA 4.0 license with the KiCad library exception](https://www.kicad.org/libraries/license/).
The provisional SW1 geometry derives from
`ergogen/footprints/ceoloide/power_switch_smd_side.js`, copyright Marco
Massarelli, 2023, with attribution to infused-kim and ceoloide, under
CC-BY-NC-SA-4.0. That geometry retains those terms and requires replacement or
verification before release. The custom TI charger and ALPS reset lands are
drawn from the manufacturers' recommended land patterns.
