# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh==5.1.1", "shapely==2.2.0", "mapbox-earcut==2.1.0", "manifold3d==3.5.4", "networkx==3.7"]
# ///
"""Removable height/width-fit hood, not the complete keyboard top frame."""

import json
from pathlib import Path

import trimesh
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "cases/thin/output"


def solid(shape, bottom, top):
    mesh = trimesh.creation.extrude_polygon(shape, top - bottom, engine="earcut")
    mesh.apply_translation([0, 0, bottom])
    return mesh


def build_cover(config, include_feet=True):
    x0, y0, x1, y1 = config["outerBoundsLegacyMm"]
    wall = config["wallThicknessMm"]
    inside_height = config["measuredAssemblyAbovePcbTopMm"] + config["verticalClearanceMm"]
    top = inside_height + config["roofThicknessMm"]
    roof = solid(box(x0, y0, x1, y1), inside_height, top)
    sides = [solid(box(x0, y0, x0 + wall, y1), 0, inside_height),
             solid(box(x1 - wall, y0, x1, y1), 0, inside_height)]
    # USB end (positive Y) stays open. At the opposite end, a lower opening
    # passes the battery wires without clamping them between wall and PCB.
    back = solid(box(x0, y0, x1, y0 + wall), 0, inside_height)
    center = config["controllerCenterXLegacyMm"]
    half_width = config["wireOpeningWidthMm"] / 2
    wire_cut = solid(box(center - half_width, y0 - 0.1,
                         center + half_width, y0 + wall + 0.1),
                     -0.1, config["wireOpeningHeightMm"])
    back = trimesh.boolean.difference([back, wire_cut], engine="manifold")
    # The outside wall lies beyond the PCB edge. Two small inward feet reach
    # onto the edge of the PCB, below the socketed controller, to seat the hood.
    feet = [solid(box(220.9, start_y, x1, start_y + 3), 0, 0.8)
            for start_y in (y0, y1 - 3)]
    mesh = trimesh.boolean.union([roof, *sides, back, *(feet if include_feet else [])], engine="manifold")
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(mesh.split()) == 1
    return mesh


def main():
    config = json.loads((ROOT / "cases/thin/left-cover.json").read_text())
    inside_height = config["measuredAssemblyAbovePcbTopMm"] + config["verticalClearanceMm"]
    x0, y0, x1, y1 = config["outerBoundsLegacyMm"]
    wall = config["wallThicknessMm"]
    mesh = build_cover(config)
    # Print roof down: a flat bed contact and vertical walls need no supports.
    mesh.apply_transform(trimesh.transformations.rotation_matrix(3.141592653589793, [1, 0, 0]))
    mesh.apply_translation(-mesh.bounds[0])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    filename = "knuckles_left_controller_battery_cover_fit_prototype.stl"
    mesh.export(OUTPUT / filename)
    checked = trimesh.load(OUTPUT / filename)
    assert checked.is_watertight and checked.is_winding_consistent and checked.volume > 0
    assert len(checked.split()) == 1
    report = {
        "file": filename,
        "status": "Loose fit prototype; no fasteners or full top frame",
        "sizeMm": checked.extents.tolist(),
        "insideHeightAbovePcbMm": inside_height,
        "insideWidthMm": x1 - x0 - 2 * wall,
        "insideLengthToOpenUsbEndMm": y1 - y0 - wall,
        "watertight": True,
        "connectedBodies": 1,
        "printOrientation": "Already oriented roof down; leave the large flat roof on the bed",
        "pending": ["Battery width and wire clearance", "USB plug clearance", "Adjacent key travel", "Seating feet clear the controller sockets"],
        "parameters": config
    }
    (OUTPUT / "left-cover-dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Generated {filename}: {checked.extents.round(3).tolist()} mm; inside height {inside_height} mm; watertight, one solid")


if __name__ == "__main__":
    main()
