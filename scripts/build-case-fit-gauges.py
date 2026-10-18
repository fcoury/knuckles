# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh==5.1.1", "shapely==2.2.0", "mapbox-earcut==2.1.0"]
# ///
"""Export footprint-only gauges for the assembled 18.5 mm board revision."""

import json
from pathlib import Path

import trimesh
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = json.loads((ROOT / "cases/thin/legacy-18.5.json").read_text())
OUTPUT = ROOT / "cases/thin/output"
CLEARANCE = 0.3
WALL = 1.35
HEIGHT = 1.0
HOLE_RADIUS = 1.1


def main():
    pcb = Polygon(REFERENCE["outline"])
    assert pcb.is_valid and not pcb.interiors, "Reference must be one simple outline"
    pieces = [pcb.buffer(CLEARANCE + WALL).difference(pcb.buffer(CLEARANCE))]
    holes = []
    for hole in REFERENCE["mountHoles"]:
        center = Point(hole["x"], hole["y"])
        boundary = nearest_points(center, pcb.exterior)[1]
        distance = center.distance(boundary)
        end = Point(boundary.x + (boundary.x - center.x) / distance,
                    boundary.y + (boundary.y - center.y) / distance)
        pieces.extend([center.buffer(2.5), LineString([center, end]).buffer(0.8, cap_style="flat")])
        holes.append(center.buffer(HOLE_RADIUS))
    gauge = unary_union(pieces).difference(unary_union(holes))
    assert gauge.geom_type == "Polygon" and gauge.is_valid, "Gauge must be one connected part"
    assert len(gauge.interiors) == len(holes) + 1, "Mounting holes must stay open"

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"sourceCommit": REFERENCE["sourceCommit"], "clearanceMm": CLEARANCE,
              "wallMm": WALL, "heightMm": HEIGHT, "mountingHoleDiameterMm": 2 * HOLE_RADIUS,
              "parts": {}}
    for side in ("left", "right"):
        planar = gauge if side == "left" else affinity.scale(gauge, xfact=-1, origin=(0, 0))
        min_x, min_y, _, _ = planar.bounds
        planar = affinity.translate(planar, xoff=-min_x, yoff=-min_y)
        mesh = trimesh.creation.extrude_polygon(planar, height=HEIGHT, engine="earcut")
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        name = f"knuckles_{side}_footprint_gauge.stl"
        mesh.export(OUTPUT / name)
        report["parts"][side] = {"file": name, "sizeMm": mesh.extents.tolist(),
                                 "watertight": True, "volumeMm3": float(mesh.volume)}
        print(f"Generated {name}: {mesh.extents.round(3).tolist()} mm")
    (OUTPUT / "dimensions.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
