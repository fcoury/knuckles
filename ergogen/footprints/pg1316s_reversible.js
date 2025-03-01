module.exports = {
  params: {
    designator: "S",
    side: "F",
    reversible: false, // New parameter to control reversibility
    from: { type: "net", value: undefined },
    to: { type: "net", value: undefined },
    P3: { type: "net", value: "" },
  },
  body: (p) => {
    const fp = [];
    const flip = p.side === "B";
    if (!flip && p.side !== "F") throw new Error("unsupported side: " + p.side);

    // Determine footprint name based on reversibility
    const footprintName = p.reversible
      ? "CPG1316S01D02_reversible"
      : "CPG1316S01D02";
    fp.push(`(footprint "${footprintName}"`);
    fp.push(p.at);
    fp.push(`(layer ${(flip ? "B" : "F")}.Cu)`);
    fp.push(`(attr smd)`);

    fp.push(
      `(property "Reference" "${p.ref}" ${p.ref_hide} (at 0 0 ${p.r}) (layer "${p.side}.SilkS") (effects (font (size 1 1) (thickness 0.15))${
        p.side === "B" ? " (justify mirror)" : ""
      }))`,
    );

    // Pads
    fp.push(
      `(pad "1" thru_hole rect (at ${(flip
        ? 2.5
        : -2.5)} 2.65 ${p.r}) (size 1.55 2) (drill 0.5) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (thermal_bridge_angle 45) ${p.from})`,
    );
    fp.push(
      `(pad "2" thru_hole rect (at ${(flip
        ? -2.5
        : 2.5)} 2.65 ${p.r}) (size 1.55 2) (drill 0.5) (layers "*.Cu" "*.Mask") (remove_unused_layers no) (thermal_bridge_angle 45) ${p.to})`,
    );

    // P3 pads - handle differently based on reversibility
    if (p.reversible) {
      // Add all P3 pads for both sides when reversible
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "F"
            : "B")}.Cu" "${(flip ? "F" : "B")}.Paste" "${(flip
            ? "F"
            : "B")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "F"
            : "B")}.Cu" "${(flip ? "F" : "B")}.Paste" "${(flip
            ? "F"
            : "B")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "F"
            : "B")}.Cu" "${(flip ? "F" : "B")}.Paste" "${(flip
            ? "F"
            : "B")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "F"
            : "B")}.Cu" "${(flip ? "F" : "B")}.Paste" "${(flip
            ? "F"
            : "B")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
    } else {
      // Only add P3 pads for current side when not reversible
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? 6.35
          : -6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} -6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
      fp.push(
        `(pad "3" smd rect (at ${(flip
          ? -6.35
          : 6.35)} 6 ${p.r}) (size 2 2) (layers "${(flip
            ? "B"
            : "F")}.Cu" "${(flip ? "B" : "F")}.Paste" "${(flip
            ? "B"
            : "F")}.Mask") (thermal_bridge_angle 45) ${p.P3})`,
      );
    }

    // Edge.Cuts
    fp.push(
      `(fp_circle (center -5.8 2.75) (end ${(flip
        ? 5.3
        : -5.3)} 2.75) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))`,
    );
    fp.push(
      `(fp_circle (center -5.781 -2.773) (end ${(flip
        ? 6.381
        : -6.381)} -2.773) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))`,
    );
    fp.push(
      `(fp_circle (center 5.8 -2.75) (end ${(flip
        ? -6.4
        : 6.4)} -2.75) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))`,
    );
    fp.push(
      `(fp_circle (center 5.819 2.727) (end ${(flip
        ? -5.319
        : 5.319)} 2.727) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))`,
    );

    // Fabrication layers - add both sides only when reversible
    if (p.reversible) {
      // B.Fab (will be F.Fab when flipped)
      fp.push(
        `(fp_rect (start ${(flip ? 7.981 : -7.981)} -8.023) (end ${(flip
          ? -8.019
          : 8.019)} 7.977) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "F.Fab"
            : "B.Fab")}))`,
      );
      fp.push(
        `(fp_rect (start ${(flip ? 6.731 : -6.731)} -6.523) (end ${(flip
          ? -6.769
          : 6.769)} 6.477) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "F.Fab"
            : "B.Fab")}))`,
      );
      fp.push(
        `(fp_poly (pts (xy ${(flip ? 3.781 : -3.781)} -3.523) (xy ${(flip
          ? 3.781
          : -3.781)} -1.673) (xy ${(flip ? 3.281 : -3.281)} -1.173) (xy ${(flip
            ? -2.219
            : 2.219)} -1.173) (xy ${(flip ? -2.219 : 2.219)} -3.923) (xy ${(flip
            ? 2.181
            : -2.181)} -3.923) (xy ${(flip
            ? 2.181
            : -2.181)} -3.523)) (stroke (width 0.1) (type solid)) (fill none) (layer ${(flip
            ? "F.Fab"
            : "B.Fab")}))`,
      );

      // F.Fab (will be B.Fab when flipped)
      fp.push(
        `(fp_rect (start ${(flip ? 8 : -8)} 8) (end ${(flip
          ? -8
          : 8)} -8) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
      fp.push(
        `(fp_rect (start ${(flip ? 6.75 : -6.75)} -6.5) (end ${(flip
          ? -6.75
          : 6.75)} 6.5) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
      fp.push(
        `(fp_poly (pts (xy ${(flip ? -3.8 : 3.8)} -3.5) (xy ${(flip
          ? -3.8
          : 3.8)} -1.65) (xy ${(flip ? -3.3 : 3.3)} -1.15) (xy ${(flip
            ? 2.2
            : -2.2)} -1.15) (xy ${(flip ? 2.2 : -2.2)} -3.9) (xy ${(flip
            ? -2.2
            : 2.2)} -3.9) (xy ${(flip
            ? -2.2
            : 2.2)} -3.5)) (stroke (width 0.1) (type solid)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
    } else {
      // Only add fabrication layer for current side when not reversible
      fp.push(
        `(fp_rect (start ${(flip ? 8 : -8)} 8) (end ${(flip
          ? -8
          : 8)} -8) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
      fp.push(
        `(fp_rect (start ${(flip ? 6.75 : -6.75)} -6.5) (end ${(flip
          ? -6.75
          : 6.75)} 6.5) (stroke (width 0.1) (type default)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
      fp.push(
        `(fp_poly (pts (xy ${(flip ? -3.8 : 3.8)} -3.5) (xy ${(flip
          ? -3.8
          : 3.8)} -1.65) (xy ${(flip ? -3.3 : 3.3)} -1.15) (xy ${(flip
            ? 2.2
            : -2.2)} -1.15) (xy ${(flip ? 2.2 : -2.2)} -3.9) (xy ${(flip
            ? -2.2
            : 2.2)} -3.9) (xy ${(flip
            ? -2.2
            : 2.2)} -3.5)) (stroke (width 0.1) (type solid)) (fill none) (layer ${(flip
            ? "B.Fab"
            : "F.Fab")}))`,
      );
    }

    fp.push(`(version 20240108)`);
    fp.push(`(generator "pcbnew")`);
    fp.push(`(generator_version "8.0")`);
    fp.push(
      `(model "models/PG1316S--装配体.STEP" (offset (xyz -4.75 -6.25 -10.25)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))`,
    );

    fp.push(`)`);

    return fp.join("\n");
  },
};
