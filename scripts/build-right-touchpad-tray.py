# /// script
# requires-python = ">=3.11"
# dependencies = ["trimesh==5.1.1", "shapely==2.2.0", "mapbox-earcut==2.1.0", "manifold3d==3.5.4", "networkx==3.7"]
# ///
"""Right tray with an outboard holder support; physical fit remains provisional."""

import importlib.util
import json
from pathlib import Path

import trimesh
from shapely.geometry import Polygon, box

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("thin_trays", Path(__file__).with_name("build-thin-trays.py"))
trays = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trays)
SUPPORT_GAP = 0.2


def main():
    measured = json.loads((ROOT / "cases/thin/right-touchpad.json").read_text())
    pcb = Polygon(trays.REFERENCE["outline"])
    # Work in the unmirrored legacy coordinates until exporting the right half.
    edge_x = pcb.bounds[2]
    far_x = edge_x + measured["overhangBeyondPcbEdgeMm"]
    near_x = far_x - measured["holderAcrossPcbEdgeMm"]
    center_y = measured["holderCenterY"]
    half_length = measured["holderAlongPcbEdgeMm"] / 2
    holder = box(near_x, center_y - half_length, far_x, center_y + half_length)
    # Extra footprint clearance is separate from the future support/contact fit.
    extension = holder.buffer(0.6, join_style="round")
    floor_outline = pcb.buffer(trays.XY_CLEARANCE + trays.WALL).union(extension)
    assert floor_outline.geom_type == "Polygon" and floor_outline.is_valid
    assert floor_outline.covers(holder)
    mesh = trays.build_tray(floor_outline=floor_outline)
    # Contact the middle of the holder's outside rim, away from its corner
    # screws and the central electronics/cable opening. Keep a small fitting
    # gap to avoid lifting the controller out of its sockets on the first fit.
    support = box(far_x - 2.4, center_y - 10, far_x - 0.6, center_y + 10)
    pcb_top = trays.PCB_BOTTOM + trays.PCB_THICKNESS
    support_top = pcb_top + measured["holderUndersideAbovePcbTopMm"] - SUPPORT_GAP
    assert holder.covers(support) and support.disjoint(pcb)
    solids = [mesh, trays.extrude(support, trays.FLOOR, support_top)]
    ribs = []
    for offset in (-9.1, 9.1):
        rib = box(edge_x + 0.6, center_y + offset - 0.9,
                  far_x - 0.6, center_y + offset + 0.9)
        assert floor_outline.covers(rib) and rib.disjoint(pcb)
        ribs.append(rib)
        solids.append(trays.extrude(rib, trays.FLOOR, trays.RIM_TOP))
    mesh = trimesh.boolean.union(solids, engine="manifold")
    # Export coordinate convention matches the existing right tray (mirrored X).
    mesh.apply_transform(trimesh.transformations.scale_matrix(-1, direction=[1, 0, 0]))
    mesh.apply_translation([-mesh.bounds[0][0], -mesh.bounds[0][1], 0])
    name = "knuckles_right_touchpad_supported_tray_prototype.stl"
    trays.OUTPUT.mkdir(parents=True, exist_ok=True)
    mesh.export(trays.OUTPUT / name)
    checked = trimesh.load(trays.OUTPUT / name)
    assert checked.is_watertight and checked.is_winding_consistent and checked.volume > 0
    assert len(checked.split()) == 1
    report = {
        "status": "Supported tray prototype; physical holder position/contact fit unverified; no top cover",
        "measurements": measured,
        "file": name,
        "sizeMm": checked.extents.tolist(),
        "watertight": True,
        "connectedBodies": 1,
        "floorMm": trays.FLOOR,
        "supportTopAboveDeskMm": support_top,
        "supportGapMm": SUPPORT_GAP,
        "supportBoundsLegacyMm": list(support.bounds),
        "touchSurfaceAboveDeskMm": trays.PCB_BOTTOM + trays.PCB_THICKNESS + measured["touchSurfaceAbovePcbTopMm"],
        "holderBoundsLegacyMm": list(holder.bounds),
        "pending": ["Physical check of holder position along controller edge", "Confirm support meets flat holder rim and clears screws/cable"]
    }
    (trays.OUTPUT / "right-touchpad-dimensions.json").write_text(json.dumps(report, indent=2) + "\n")
    write_preview(pcb, floor_outline, holder, support, ribs, trays.OUTPUT / "right-touchpad-layout.svg")
    print(f"Generated {name}: {checked.extents.round(3).tolist()} mm; watertight, one solid")


def write_preview(pcb, floor_outline, holder, support, ribs, path):
    """True-scale top view with mirrored X; no perspective obscures the overhang."""
    min_x, min_y, max_x, max_y = floor_outline.bounds
    def polygon(shape, fill, stroke, dash=""):
        points = " ".join(f"{max_x-x+5:.3f},{max_y-y+5:.3f}" for x, y in shape.exterior.coords)
        return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="0.35" stroke-dasharray="{dash}"/>'
    width, height = max_x - min_x + 10, max_y - min_y + 26
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           polygon(floor_outline, "#dce4ec", "#45596b"),
           polygon(pcb, "#9acbb1", "#26704b"),
           polygon(holder, "#303944", "#111827", "1,1")]
    for rib in ribs:
        svg.append(polygon(rib, "#b5c5d7", "#45596b"))
    svg.append(polygon(support, "#f3a44d", "#a65a00"))
    for h in trays.REFERENCE["mountHoles"]:
        svg.append(f'<circle cx="{max_x-h["x"]+5}" cy="{max_y-h["y"]+5}" r="1.725" fill="white" stroke="#26704b" stroke-width="0.25"/>')
    svg.extend([f'<text x="5" y="{height-12}" font-family="sans-serif" font-size="3">Right base: green PCB / dark holder / orange raised support</text>',
                f'<text x="5" y="{height-6}" font-family="sans-serif" font-size="3">Holder position provisional; support has 0.2 mm fitting gap</text>', '</svg>'])
    path.write_text("\n".join(svg) + "\n")


if __name__ == "__main__":
    main()
