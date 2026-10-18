# Thin case prototypes

These parts target the older 18.5 mm key-pitch Zeph v1.0 PCBs, using the
historical outline and five mounting holes in `legacy-18.5.json`.

Current printable STL snapshots and top-view layouts are included in `prints/`.
The full left top shell and supported right touchpad tray are the latest upper
shell and right base prototypes. Their physical fit remains under validation;
the user confirmed the basic left tray fits. Regenerating writes fresh files to
`output/`; refresh the snapshots in `prints/` when changing a design.

Generate the footprint gauges and basic open-top trays:

```sh
uv run scripts/build-case-fit-gauges.py
uv run scripts/build-thin-trays.py
```

The trays have a 1.2 mm floor, 1.8 mm space below the PCB (1.5 mm measured
components plus 0.3 mm clearance), and a 3.8 mm overall rim height. Remove
the rubber feet before fitting. Check the assembled PCB rests on all five
supports without rocking or pressing on components before adding screws.

## Right touchpad base

```sh
uv run scripts/build-right-touchpad-tray.py
```

`right-touchpad.json` records the user's holder dimensions, overhang and touch
surface height. The supported tray retains the existing holder and leaves the
controller bay open. It has no top cover yet. The earlier
`knuckles_right_touchpad_base_fit_prototype.stl` is superseded by
`knuckles_right_touchpad_supported_tray_prototype.stl`.

The provisional holder center is aligned with the legacy nice!nano center at
Ergogen Y = -72.12 mm. The outside edge is located from the measured 28.55 mm
overhang. The rounded footprint extends 0.6 mm beyond the holder. The user measured
11.6 mm from PCB top to glass top, 5.6 mm from glass top to holder underside, and
7.6 mm from glass top to screw tip. Thus the holder underside is 6.0 mm above PCB
top and the screw tips 4.0 mm above it.

A 1.8 mm thick, 20 mm long wall supports the middle of the outboard holder rim;
two low ribs stiffen the floor extension. The wall stops 0.2 mm short of the
nominal underside (10.4 mm above the tray bottom) to avoid lifting the controller
on the first fit. This small gap can be checked with a 0.2 mm nonconductive shim
after verifying the holder seats correctly. The support avoids the corner screw
areas and central cable opening by design, but their actual clearance and the
holder's position still require a physical fit check. Do not force the holder
down onto a support that lifts or tilts it.

Outputs, mesh-check reports and a top-view SVG are written to `output/` (ignored
by Git). Mesh checks establish closed, connected geometry, not physical fit.

## Left controller and battery cover

```sh
uv run scripts/build-left-controller-cover.py
```

This small loose-fit hood checks the enclosure around the existing controller
and battery before adding the full keyboard top frame or fasteners. Its inside
height is 8.5 mm above the PCB (8.0 mm measured assembly plus 0.5 mm clearance),
with a 1.2 mm roof and 1.35 mm walls. Horizontal placement comes from the legacy
controller location and photos; it still requires a physical check.

The STL is already oriented roof down for printing without supports. Leave the
large flat roof on the bed. After printing, turn it over and place the completely
open end toward USB. The opposite end has the lower battery-wire opening. Two
small feet on the outer wall reach onto the PCB edge. Check these clear the
controller/socket assembly, the battery fits without pressure, USB can plug in,
and adjacent keys move freely. Do not force or fasten this loose fit prototype.

## Complete left top shell

```sh
uv run scripts/build-left-top-shell.py
```

`knuckles_left_full_top_shell_prototype.stl` is the complete upper half: a panel
around all 27 keys, an outer skirt over the existing tray, and an integrated
controller/battery hood. The small separate hood above is only a fit coupon;
use this complete shell when testing the overall top.

The skirt has 0.3 mm clearance per side around the tested tray. Its internal
ledge seats on the tray's rim. The key panel is 1.2 mm thick, starting 0.3 mm
above PCB top, with 18.0 by 17.5 mm key openings. The existing PCB screw heads,
power/reset area and USB approach have openings. At the controller, the hood
retains the 8.5 mm inside height. This is a gravity/slip fit for validation, with
no locking clips yet; it must not be treated as a secure transport enclosure.

Print in the exported orientation, skirt down, using supports under the elevated
panel and hood. Use the Arachne wall generator for the narrow 0.5 mm webs between
columns. A 0.2 mm layer height is suitable for this first fit. Supports in the
key openings must be removed before installation. Unlike the separate small
hood, this integrated shell is not a support-free print.

Generation checks one connected, watertight mesh after STL round trip, plus no
solid interference with the original tray or the nominal keycap travel volumes.
Actual battery width, wire/socket clearance, screw heads and key movement still
require inspection on the assembled board. Do not force the shell onto it.
