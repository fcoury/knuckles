# Engineering review and routing handoff

Reviewed 2026-10-18. This checkpoint establishes the electrical architecture,
package/pin contracts, buildable firmware and initial mechanical placement.
It does not establish signal integrity, thermal performance, radio performance,
USB compliance or hardware operation. Routing and prototype evidence remain
necessary before ordering an assembled keyboard.

## Corrections made during review

| Initial issue | Implemented correction | Evidence/check |
| --- | --- | --- |
| BQ25185 fixed timer versus a 500 mAh pack at 20 mA | BQ25186, programmable 12 h timer and 20/50/100 mA profiles | TI SLUSF69A register map; policy tests |
| MSK12C02 assigned an Alps footprint | Stocked Alps SSSS811101 / C109335, matched to its own land and contact drawing | Alps sources in sources.json |
| Direct/default charge enable | VBUS pull-up on CE, Q3 isolation, GPIO pulldown, R12 DNP interlock | Netlist/physical-pad contracts |
| ADC divider settling too slowly | 10 kΩ / 10 kΩ and 100 nF, gated by PMOS/NMOS | 0.5 ms time constant versus ZMK's 10 ms wait |
| Missing module USB reference components | 27 Ω data resistors and revised decoupling | Raytac Ver. L, normal-voltage reference |
| Nominal capacitors lost most capacitance under bias | 22 µF/25 V 0805 C45783 at C2/C6/C8/C10/C11 | Manufacturer DC-bias curves retained in references/capacitor-bias.json |
| Sensor/battery metal above radio antenna | Antenna toward inner edge, expanded all-copper keepout, proposed forward TPS43 shift | Placement study; physical verification still required |
| Left peripheral had no USB power negotiation | CDC USB device on left; normal ZMK HID on right | Both firmware variants compile |
| Charger watchdog could interrupt DFU | Custom bootloader disables charging and watchdog, limits input current | Bootloader compiles; bench recovery test remains |

## Power and battery contract

The circuit accepts a **protected single-cell LiPo with a 4.2 V maximum charge
voltage**. Capacity is not sufficient to verify a pack. Obtain its charge-current,
voltage and temperature ratings and connector polarity. Do not substitute a
4.35 V chemistry, primary cell, or series pack.

The MCU and TPS43 receive regulated 3.3 V. Module VDD/pad 28 and VDDH/pad 30
connect to 3.3 V; DCCH/pad 31 is unconnected; VBUS/pad 32 senses USB. The module's
REG1 DC/DC is enabled; the high-voltage REG0 DC/DC is disabled. The external
regulator still needs its own short switching loop and decoupling.

R11 holds charger CE high from VBUS. Q3 pulls it low only when CHG_ALLOW is high;
R10 holds Q3 off during reset. R12 remains DNP until bring-up authorizes charging.
This arrangement prevents 5 V from reaching the MCU enable pin and prevents the
BQ25186's default charging configuration from charging a small cell at startup.
The mechanical power switch disables the 3.3 V regulator. **Charging requires
that switch to be on**, so firmware can authorize and supervise it.

| Pack/profile | Current | Ideal capacity/current interval | Timer |
| --- | --- | --- | --- |
| 110 mAh | 20 mA | 5.5 h | 12 h |
| 250 mAh | 50 mA | 5 h | 12 h |
| 500 mAh | 100 mA | 5 h | 12 h |

These intervals exclude precharge, CV taper, temperature reduction and input
limiting. They are not promised full-charge times. In cold conditions the
charger reduces current; a safety timeout remains a fault, not a reason to
restart the charge cycle automatically. Other capacities require deliberate
profile selection and review against the actual cell rating.

Firmware sets 4.2 V, 3.0 V discharge UVLO, 500 mA discharge overcurrent limit,
20% precharge, 10% termination, 0–45 °C hot/cold boundaries and the 12 h timer.
The IC's discharge limit is not a replacement for cell protection. A 10 kΩ,
beta-3435 NTC connects from TS/MR to ground and must contact the cell thermally.
The default firmware does not authorize charging. It also checks for an open
thermistor before enabling; ordinary temperature limits remain enforced in
hardware. Thermistor tolerances and the selected cell's allowed temperature
window require bench confirmation.

The 10 kΩ battery divider presents 5 kΩ Thevenin resistance to its 100 nF filter:
τ = 0.5 ms. ZMK waits 10 ms after enabling the divider, giving 20 time constants.
The PMOS disconnects the battery-side divider when the MCU is off and the
NMOS isolates its control pin from battery voltage. Sampling draws about
210 µA at 4.2 V only while enabled.

Samsung's typical DC-bias curves show the original 10 µF/10 V 0603 part at
about 3.20 µF at 4.5 V. The selected 22 µF/25 V 0805 part is about 11.77 µF at
4.5 V and 14.90 µF at 3.3 V. Applying a planning margin of 20% tolerance and
15% temperature loss gives about 8.0 and 10.1 µF respectively, before aging.
These calculations use typical curves, not guaranteed minimum data. Validate
startup, radio/TPS load steps and ripple on the assembled power stage.
C10 and C11 provide parallel output capacitance. C9 remains 100 nF at VINA.

## USB behavior

The firmware advertises 250 mA (`USB_MAX_POWER=125` in this Zephyr version).
BQ25186 input limiting starts at 100 mA and becomes 200 mA after USB
configuration. The 200 mA setting can reach 220 mA per TI's tolerance table;
250 mA leaves headroom for the module's separate USB regulator and pull-up.
Charging is authorized only after configuration, while physical VIN is good.
Consequently **this prototype charges from a USB host, not a charge-only wall
adapter**. Supporting wall chargers requires source/current detection or a
separately reviewed conservative mode; it is not inferred from USB-C presence.

Direct VBUS capacitance is 4.7 + 2.2 + 0.1 = 7.0 µF nominal, leaving tolerance
headroom below 10 µF. This does not prove inrush compliance: scope the startup
current, including the charger power-path and downstream capacitance. Raytac's
reference uses 10 µF at VBUS; the redistributed 7 µF must be validated at the
module under cable/load transients. DECUSB decoupling is inside the module.

On suspend, charging stops and SYS is forced to battery. TI documents that
force-battery is ignored below battery UVLO. In that case firmware disables the
watchdog and switches SYS off; reconnect USB to recover. An interrupt and a
30 s health poll supervise the charger. Unexpected register changes, I2C errors
and safety-timeout reports disable charging. Routine polls do not rewrite
charge settings or toggle CE. If the I2C bus is unusable, the hardware watchdog
can reset SYS; recovery needs testing with the assembly interlock still open.

System-off sleep is disabled in these initial builds to keep watchdog servicing
active. Runtime idle remains available. Battery life has not been measured.
The DFU bootloader disables charging throughout, uses a 100 mA input limit and
powers SYS off on USB suspend. Reconnect USB if the computer sleeps during DFU.
Measure suspend current and transitions; no compliance claim is made from code.

## Mechanical integration

The matrix and five main mounting holes come from the selected spacing's fresh
Ergogen output. Reversible back-side matrix lands and nice!nano circuitry are
removed; right-hand geometry is reflected without mirroring physical package
pad numbers. The per-half netlist checks confirm all 27 row/column combinations.

The controller occupies the existing inner-edge bay. The module is rotated so
its antenna faces the inside edge. Copper keepouts apply to all four copper
layers. Route neither ground nor signals through the antenna exclusion, and
keep battery foil, screws, touchpad metal and cables out of that volume above
and below the PCB. Validate the completed enclosure's radio behavior.

The TPS43 holder was previously measured around 46.96 × 43.95 mm with 28.55 mm
overhang. The proposed center shifts about 7 mm toward USB to separate its
metal from the radio region. The holder mounts to the case; MH1/MH2, previously
used by the controller cover, are removed. Confirm the holder and screw heights,
USB plug insertion, cable bend, power switch travel and full keycap travel.
The old case/controller cover is not automatically compatible.

Back-side components include the ADC circuit, isolated charge gate, several
passives and SWD/NTC pads. The largest selected back-side capacitor is up to
1.4 mm thick before solder allowance. Provide tray clearance and mechanical
support without pressing on components. A 500 mAh pack's physical dimensions
are still unknown; reserve case space only after selecting the pack.

## Routing order and acceptance

1. Select the actual JLC four-layer 1.6 mm stack and fabrication/assembly process.
   Use F.Cu for the critical local power/USB routes, In1.Cu as a continuous ground
   reference, In2.Cu for power/secondary signals and B.Cu for matrix/secondary
   routing. Never pour copper in the antenna area.
2. Route U3, L1 and local input/output capacitors manually as one small cell.
   Keep L1/L2 switch nodes short and compact; join PGND and capacitor returns
   locally, give the exposed pad a sound ground/thermal connection, and take
   feedback from the quiet regulated output. Do not run ADC or USB under switch
   nodes. Placement is provisional and may move to achieve the correct loops.
3. Route U2 IN/SYS/BAT and its capacitors with short power paths. Keep thermal
   vias and solder-paste design compatible with the assembler's WSON process.
   Do not assume arbitrary open vias in the exposed pad are assembly-safe.
4. Route USB as 90 Ω differential pairs using the selected stackup calculator.
   Keep the ESD device at the connector and 27 Ω resistors near the module.
   Join the receptacle's duplicate D+/D− pins with minimal stubs. Maintain a
   ground reference and return paths; avoid unnecessary vias and meanders.
5. Route power/grounds, independent I2C buses, reset/SWD and the gated ADC. Keep
   the ADC trace away from switching nets. Then route the matrix. Freerouting
   can assist with the matrix after critical routes are locked; a successful
   autorouter run is not a power/RF/USB review.
6. Refill zones and require zero unconnected items, no clearance/short/keepout
   errors, and reviewed silkscreen/library warnings. Check schematic parity,
   both spacings, both hands, connector polarity, DNP handling, CPL rotations,
   package heights and enclosure clearance before producing manufacturing files.

A stock Raytac listing is not a reservation. C5118826 was unavailable in the
saved JLC snapshot. U2 is the stocked **BQ25186DLHR / C44639442** listing;
other similarly named listings are not interchangeable procurement evidence.
Obtain module sourcing and an assembly quote before planning an order.

L1 also needs an exact-variant check: the catalog lists SWPA3015S1R5MT, while
Sunlord's public table gives SWPA3015S1R5NT (30% tolerance, 2.30 A saturation
rating and 1.70 A thermal-current rating). Do not silently transfer those
ratings to the MT variant. Obtain its specification or substitute the exact
published part after reviewing sourcing, footprint and worst-case peak current.
This is a procurement/release gate, not a verified rating for C83434.

## Bring-up sequence

Keep R12 open. Inspect and measure resistance/polarity before power. Test USB
input and regulated 3.3 V with a current-limited supply, then SWD access and the
custom bootloader. Confirm reset/double-tap recovery and USB enumeration.
Check all 27 keys on each half, the BLE split link, host Bluetooth profiles and
TPS43 motion/buttons/scrolling. Measure radio and touchpad activity transients.

Use a controlled battery/supply setup to verify ADC voltage, UVLO, input limits,
watchdog, suspend with a charged/empty/absent battery, and USB reconnection.
Then validate the actual pack and NTC, select its profile, enable charging in
a test build and fit R12. Measure real CC/CV/termination, hot/cold/open/short NTC
behavior and fault persistence. Do not use firmware compilation as evidence of
those analog behaviors.

## Handoff between models

6.1-sol can continue the constrained implementation from this checkpoint:
layout work under the rules above, mechanical gauges, scripts, manufacturing
exports once release gates pass, and bench-test logging. Keep a demanding review
for the finished power/USB/RF routing and any architecture changes. This review
cannot be completed before those routes and physical measurements exist.
