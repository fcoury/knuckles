# Engineering review only - not approved for ordering

Gerbers and drill files passed the retained KiCad physical/connectivity gate.
This does not establish assembly orientation, impedance, power, RF or USB compliance.
CPL rotations are KiCad angles, pending comparison with the assembler's library
and pin-1/polarity preview on both sides. Do not submit them as approved rotations.
Keyboard switches/diodes, bare pogo/NTC pads and all DNP parts are excluded from
controller PCBA. R12 MUST remain unpopulated; charging remains disabled.

Outstanding gates: exact radio module procurement/consignment acceptance;
JLC04161H-3313 stack and controlled-impedance confirmation; DFM/stencil and via
tenting review; retained silkscreen/library warnings; physical touchpad/case and
battery clearances; current-limited bench bring-up and cell/NTC validation.
Use ENGINEERING.md for the bring-up sequence. No order or quote was submitted.
