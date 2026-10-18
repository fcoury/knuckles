# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh==5.1.1", "shapely==2.2.0", "mapbox-earcut==2.1.0", "manifold3d==3.5.4", "networkx==3.7"]
# ///
"""First-fit trays for the legacy PCB; controller/battery/TPS43 remain uncovered."""

import json
from pathlib import Path

import trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = json.loads((ROOT / "cases/thin/legacy-18.5.json").read_text())
OUTPUT = ROOT / "cases/thin/output"
FLOOR = 1.2
UNDERSIDE_PROTRUSION = 1.5
VERTICAL_CLEARANCE = 0.3
PCB_THICKNESS = 1.6
XY_CLEARANCE = 0.3
WALL = 1.35
PCB_BOTTOM = FLOOR + UNDERSIDE_PROTRUSION + VERTICAL_CLEARANCE
RIM_TOP = PCB_BOTTOM + 0.8
PILOT_RADIUS = 0.85
PILOT_BOTTOM = 0.6


def extrude(shape, bottom, top):
    mesh = trimesh.creation.extrude_polygon(shape, top - bottom, engine="earcut")
    mesh.apply_translation([0, 0, bottom])
    return mesh


def build_tray(floor_outline=None):
    pcb = Polygon(REFERENCE["outline"])
    outer = pcb.buffer(XY_CLEARANCE + WALL)
    if floor_outline is None:
        floor_outline = outer
    cavity = pcb.buffer(XY_CLEARANCE)
    # Keep the entire controller edge open for USB, reset, switch, and wiring.
    # These limits come from the legacy controller-area outline, in Ergogen XY.
    open_bay = box(201.0, -113.0, 230.0, -45.0)
    rim = outer.difference(cavity).difference(open_bay)
    supports = unary_union([Point(h["x"], h["y"]).buffer(2.8)
                            for h in REFERENCE["mountHoles"]])
    pilots = unary_union([Point(h["x"], h["y"]).buffer(PILOT_RADIUS)
                          for h in REFERENCE["mountHoles"]])
    solids = [extrude(floor_outline, 0, FLOOR)]
    for shape in ([rim] if rim.geom_type == "Polygon" else rim.geoms):
        solids.append(extrude(shape, FLOOR, RIM_TOP))
    for shape in supports.geoms:
        solids.append(extrude(shape, FLOOR, PCB_BOTTOM))
    tray = trimesh.boolean.union(solids, engine="manifold")
    cutters = [extrude(shape, PILOT_BOTTOM, PCB_BOTTOM + 0.1) for shape in pilots.geoms]
    tray = trimesh.boolean.difference([tray, *cutters], engine="manifold")
    assert tray.is_watertight and tray.is_winding_consistent and tray.volume > 0
    assert len(tray.split()) == 1, "Tray must be one connected solid"
    return tray


def main():
    tray = build_tray()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"status": "first-fit prototype; electronics remain uncovered",
              "sourceCommit": REFERENCE["sourceCommit"], "floorMm": FLOOR,
              "measuredUndersideProtrusionMm": UNDERSIDE_PROTRUSION,
              "verticalClearanceMm": VERTICAL_CLEARANCE, "pcbUndersideAboveDeskMm": PCB_BOTTOM,
              "pcbTopAboveDeskMm": PCB_BOTTOM + PCB_THICKNESS, "rimHeightMm": RIM_TOP,
              "pilotDiameterMm": 2 * PILOT_RADIUS, "pilotDepthMm": PCB_BOTTOM - PILOT_BOTTOM,
              "parts": {}}
    for side in ("left", "right"):
        mesh = tray.copy()
        if side == "right":
            mesh.apply_transform(trimesh.transformations.scale_matrix(-1, direction=[1, 0, 0]))
        mesh.apply_translation([-mesh.bounds[0][0], -mesh.bounds[0][1], 0])
        name = f"knuckles_{side}_thin_tray_prototype.stl"
        mesh.export(OUTPUT / name)
        checked = trimesh.load(OUTPUT / name)
        assert checked.is_watertight and checked.is_winding_consistent and checked.volume > 0
        report["parts"][side] = {"file": name, "sizeMm": checked.extents.tolist(),
                                 "watertight": True, "volumeMm3": float(checked.volume)}
        print(f"Generated {name}: {checked.extents.round(3).tolist()} mm")
    (OUTPUT / "tray-dimensions.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
