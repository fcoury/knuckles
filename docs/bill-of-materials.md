# Bill of materials

Parts for one complete 54-key Knuckles wireless keyboard: two halves with
27 keys each, using nice!nano controllers. Quantities are installed quantities;
order spare switches and diodes if you want replacements during assembly.

This list covers the [18.5 mm wireless PCB ordered on 2026-10-18](../manufacturing/2026-10-18-knuckles-wireless-18.5mm/README.md).
It does not cover the original wired board or the experimental
[integrated-controller revision](../hardware/integrated-controller/README.md).

## Keyboard parts

Populate one face of each reversible PCB to make a left and a right half.
Although the PCB file contains 54 switch footprints and 54 diode footprints,
each physical board uses only 27 switches and 27 diodes.

| Part | Per half | Complete keyboard | Specification / notes |
| --- | ---: | ---: | --- |
| Wireless PCB | 1 | 2 | Same reversible PCB for both halves; use the archived manufacturing files linked above. |
| Key switches | 27 | 54 | Kailh PG1316S low-profile switches; footprint named `CPG1316S01D02`. Soldered directly to the PCB. |
| Diodes | 27 | 54 | 1N4148W in **SOD-123** packaging, matching the diode footprint. Install beneath the switches before soldering the switches. |
| Keycaps | 27 | 54 | PG1316S-compatible keycaps. Check stem compatibility and clearance at the selected key spacing. |
| Controllers | 1 | 2 | nice!nano. A matching header shape alone does not establish compatibility for another controller. |
| Controller mounting pins | 24 | 48 | Two 12-pin rows per controller, 2.54 mm pitch. Use headers for direct mounting, or compatible pins with sockets. |
| Reset buttons | 1 | 2 | Panasonic **EVQ-PUC02K** side-actuated momentary switch; the configured footprint includes locating-boss holes. |
| Power switches | 1 | 2 | Alps **SSSS811101** side-actuated SMD slide switch. Connects battery positive to the controller's RAW input. |
| Battery connectors | 1 | 2 | **JST S2B-PH-K** footprint, two pins at 2.0 mm pitch, right-angle through-hole. |
| Batteries | 1 | 2 | Single-cell rechargeable LiPo compatible with the chosen controller's battery input and charging requirements, with a mating JST-PH lead. Capacity and dimensions are not specified by this PCB; choose for the enclosure and controller. |

The switch, diode, and connector specifications come from the
[board configuration](../ergogen/config.yaml) and its footprint definitions:
[key switch](../ergogen/footprints/pg1316s_reversible.js),
[diode](../ergogen/footprints/ceoloide/diode_tht_sod123.js),
[controller](../ergogen/footprints/ceoloide/mcu_nice_nano.js),
[reset button](../ergogen/footprints/ceoloide/reset_switch_smd_side.js),
[power switch](../ergogen/footprints/ceoloide/power_switch_smd_side.js), and
[battery connector](../ergogen/footprints/ceoloide/battery_connector_jst_ph_2.js).
These identify the intended footprints, not a record of purchased parts or
bench-tested substitutes.

## Optional parts and enclosure

Choose these parts to match your controller mounting height, enclosure, and
whether you want a touchpad.

| Part | Complete keyboard | Specification / notes |
| --- | ---: | --- |
| Controller sockets | 4 × 12-position strips | Optional removable mounting, two strips per controller. Use matching pins and verify clearance for the USB connector and components. |
| Touchpad module | 1 | Optional HolyKeebs TPS43 module with the matching nice!nano adapter and holder. The adapter uses VCC, GND, SDA, and SCL. |
| Cases / bottom trays | 2 | One left and one right, matching the PCB spacing. The [thin-case prototypes](../cases/thin/README.md) target an older assembled board; their fit does not establish fit for this manufacturing revision. |
| Plates / controller covers | As required | Match the selected enclosure and key spacing; these are separate from the keyboard PCB. |
| M2 fasteners and spacers | Depends on enclosure | Five PCB support positions and two controller-cover positions per half. Select screw lengths and spacer heights for the actual case stack; the repository does not define a universal hardware kit. |
| Rubber feet | As required | Depends on the case; check clearance before adding feet to a bare PCB. |
| USB data cable | 1 or more | Connector matching your controllers; needed for flashing and USB use. |

The wireless build does not require a TRRS cable, TRRS sockets, display, or
switch hotswap sockets.

## Assembly compatibility notes

Controller orientation and connector polarity affect assembly even when the
parts fit their footprints.

- The controller has 24 solder-jumper pairs per PCB. With the controller above
  the PCB and its chip and USB connector facing down toward the PCB, bridge
  the pairs on that same PCB face. With components facing away from the PCB,
  the footprint uses bridges on the opposite face. Populate only one set;
  verify the controller pin alignment before applying power.
- The battery connector has its own reversible-footprint jumpers. Check its
  connections and the battery lead polarity against `BAT_P` and `GND`;
  connector fit alone does not establish polarity.
- Solder and test the diodes before covering them with switches. A multimeter,
  soldering iron, solder, flux, tweezers, and solder wick are assembly supplies,
  not installed BOM items.

[Back to the project README](../README.md)
