# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh==5.1.1", "shapely==2.2.0", "mapbox-earcut==2.1.0", "manifold3d==3.5.4", "networkx==3.7"]
# ///
"""Complete left slip-fit top shell with key openings and integrated battery hood."""

import importlib.util
import json
import sys
from pathlib import Path

import trimesh
from shapely.affinity import rotate, translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import set_precision

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "cases/thin/output"
sys.dont_write_bytecode = True


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


trays = module("thin_trays", "build-thin-trays.py")
hood = module("left_cover", "build-left-controller-cover.py")
SLEEVE_CLEARANCE = 0.3
PANEL_THICKNESS = 1.2
PANEL_PCB_GAP = 0.3


def pieces(shape):
    return [shape] if shape.geom_type == "Polygon" else list(shape.geoms)


def main():
    layout = json.loads((ROOT / "cases/thin/legacy-key-layout.json").read_text())
    config = json.loads((ROOT / "cases/thin/left-cover.json").read_text())
    pcb = Polygon(trays.REFERENCE["outline"])
    tray_outer = pcb.buffer(trays.XY_CLEARANCE + trays.WALL)
    sleeve_inner = tray_outer.buffer(SLEEVE_CLEARANCE)
    outside = sleeve_inner.buffer(trays.WALL)
    pcb_top = trays.PCB_BOTTOM + trays.PCB_THICKNESS
    panel_bottom = pcb_top + PANEL_PCB_GAP
    panel_top = panel_bottom + PANEL_THICKNESS
    # Leave the USB approach clear through the outer skirt and seating ledge.
    usb_access = box(201, -59, 230, -45)
    skirt = outside.difference(sleeve_inner).difference(usb_access)
    ledge = outside.difference(pcb.buffer(trays.XY_CLEARANCE)).difference(usb_access)
    keycaps, apertures = [], []
    for key in layout["keys"]:
        def placed(width, length):
            return translate(rotate(box(-width/2, -length/2, width/2, length/2),
                                    key["rotationDeg"], origin=(0, 0)), key["x"], key["y"])
        cap = placed(layout["keycapWidthMm"], layout["keycapLengthMm"])
        aperture = placed(18.0, 17.5)
        assert aperture.covers(cap)
        keycaps.append(cap)
        apertures.append(aperture)
    # Keep the actual controller/battery volume open under the raised hood.
    x0, y0, x1, y1 = config["outerBoundsLegacyMm"]
    wall = config["wallThicknessMm"]
    controller_opening = box(x0 + wall, y0, x1 - wall, -45)
    controls_opening = box(201.0, -114.0, 230.0, y0)
    screw_clearance = [Point(h["x"], h["y"]).buffer(3.0)
                       for h in trays.REFERENCE["mountHoles"]]
    cuts = unary_union([*apertures, controller_opening, controls_opening, *screw_clearance])
    panel = outside.difference(cuts).difference(usb_access)
    # A web beside the USB access becomes isolated from the perimeter once
    # the neighboring key openings are cut. Leave that gap open rather than
    # exporting an unattached sliver above the keys.
    panel = unary_union([part for part in pieces(panel) if part.intersection(ledge).area > 0])
    solids = []
    # Stack distinct horizontal layers instead of overlapping coplanar rims;
    # snap 2D vertices to 0.001 mm to avoid tiny facets in float32 STL output.
    for footprint, bottom, top in ((skirt, trays.FLOOR, trays.RIM_TOP),
                                   (ledge, trays.RIM_TOP, panel_bottom),
                                   (panel, panel_bottom, panel_top)):
        for shape in pieces(set_precision(footprint, 0.001)):
            solids.append(hood.solid(shape, bottom, top))
    cover = hood.build_cover(config, include_feet=False)
    cover.apply_translation([0, 0, pcb_top])
    solids.append(cover)
    shell = trimesh.boolean.union(solids, engine="manifold")
    assert shell.is_watertight and shell.is_winding_consistent and shell.volume > 0
    assert len(shell.split()) == 1, "Top shell must be one connected part"
    # Verify every nominal cap's vertical travel envelope is clear of the shell.
    cap_cutters = [hood.solid(cap, pcb_top, 20) for cap in keycaps]
    overlap = trimesh.boolean.intersection([shell, trimesh.boolean.union(cap_cutters, engine="manifold")], engine="manifold")
    assert overlap.is_empty or abs(overlap.volume) < 1e-5, "Shell intersects nominal keycap travel"
    # Verify the closed shell has no solid interference with the existing tray.
    tray = trays.build_tray()
    collision = trimesh.boolean.intersection([shell, tray], engine="manifold")
    assert collision.is_empty or abs(collision.volume) < 1e-5, "Shell collides with the existing tray"
    shell.apply_translation(-shell.bounds[0])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    filename = "knuckles_left_full_top_shell_prototype.stl"
    shell.export(OUTPUT / filename)
    checked = trimesh.load(OUTPUT / filename)
    assert checked.is_watertight and checked.is_winding_consistent and checked.volume > 0
    assert len(checked.split()) == 1
    report = {
        "file": filename, "status": "Full top shell fit prototype; gravity/slip fit, no locking clips yet",
        "sizeMm": checked.extents.tolist(), "keyCount": len(keycaps),
        "keyOpeningMm": [18.0, 17.5], "panelThicknessMm": PANEL_THICKNESS,
        "panelClearanceAbovePcbMm": PANEL_PCB_GAP,
        "sleeveClearancePerSideMm": SLEEVE_CLEARANCE,
        "batteryInsideHeightAbovePcbMm": 8.5,
        "watertight": True, "connectedBodies": 1,
        "nominalKeycapTravelInterferenceMm3": 0,
        "existingTrayInterferenceMm3": 0,
        "printOrientation": "As exported, skirt down; supports required under panel and hood",
        "pending": ["Physical fit and key travel", "Battery, sockets, USB plug and wire clearance", "Final retention after sleeve fit is verified"]
    }
    (OUTPUT / "left-top-shell-dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    preview(outside, panel, apertures, config, OUTPUT / "left-top-shell-layout.svg")
    print(f"Generated {filename}: {checked.extents.round(3).tolist()} mm; 27 key openings; watertight, one solid; zero tray/keycap interference")


def preview(outside, panel, apertures, config, path):
    min_x, min_y, max_x, max_y = outside.bounds
    width, height = max_x-min_x+10, max_y-min_y+25
    def drawing(shape, fill, stroke):
        def ring(coords):
            return "M " + " L ".join(f"{x-min_x+5:.3f},{max_y-y+5:.3f}" for x,y in coords) + " Z "
        data = " ".join(ring(poly.exterior.coords) + " ".join(ring(h.coords) for h in poly.interiors) for poly in pieces(shape))
        return f'<path d="{data}" fill="{fill}" stroke="{stroke}" stroke-width="0.25" fill-rule="evenodd"/>'
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>', drawing(panel,"#c2d4df","#445c6d")]
    for aperture in apertures:
        svg.append(drawing(aperture, "#ffffff", "#8196a3"))
    svg.append(drawing(box(*config["outerBoundsLegacyMm"]),"#7196ae","#284d65"))
    svg.extend([f'<text x="5" y="{height-12}" font-family="sans-serif" font-size="3">Left full top: 27 key openings + integrated controller/battery hood</text>',
                f'<text x="5" y="{height-6}" font-family="sans-serif" font-size="3">Slip-fit prototype; USB end open; supports needed for printing</text>', '</svg>'])
    path.write_text("\n".join(svg) + "\n")


if __name__ == "__main__":
    main()
