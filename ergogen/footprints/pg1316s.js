// Kailh PG1316S
// Nets
//    from: corresponds to pin 1
//    to: corresponds to pin 2
// Params
//    keycaps: default is false
//      if true, will add sized keycap box around the footprint
//

module.exports = {
  params: {
    designator: "S",
    side: "F",
    keycaps: false,
    from: undefined,
    to: undefined,
  },
  body: (p) => {
    return `
(footprint "CPG1316S01D02_mikeholscher"
  (layer "${p.side}.Cu")
  ${p.at}
  (property "Reference" "${p.ref}"
      (at 0 0 ${p.r})
      (layer "${p.side}.SilkS")
      ${p.ref_hide}
      (effects (font (size 1 1) (thickness 0.1)))
  )
  (attr smd)
  (fp_poly
    (pts
      (xy 3.8 -3.5)
      (xy 3.8 -1.65)
      (xy 3.3 -1.15)
      (xy -2.2 -1.15)
      (xy -2.2 -3.9)
      (xy 2.2 -3.9)
      (xy 2.2 -3.5)
    )
    (stroke (width 0.1) (type solid)) (fill none) (layer "Dwgs.User"))
  (fp_circle (center -5.8 2.75) (end -5.3 2.75) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))
  (fp_circle (center 5.8 -2.75) (end 6.4 -2.75) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts"))
  (fp_rect (start -8 8) (end 8 -8) (stroke (width 0.1) (type default)) (fill none) (layer "${p.side}.Fab"))
  (fp_rect (start -6.75 -6.5) (end 6.75 6.5) (stroke (width 0.1) (type default)) (fill none) (layer "${p.side}.Fab"))
  (pad "1" smd rect (at -2.5 2.65 ${p.r}) (size 1.55 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") ${p.to.str})
  (pad "2" smd rect (at 2.5 2.65 ${p.r}) (size 1.55 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") ${p.from.str})
  (pad "3" smd rect (at -6.35 -6 ${p.r}) (size 2 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (thermal_bridge_angle 45))
  (pad "3" smd rect (at -6.35 6 ${p.r}) (size 2 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (thermal_bridge_angle 45))
  (pad "3" smd rect (at 6.35 -6 ${p.r}) (size 2 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (thermal_bridge_angle 45))
  (pad "3" smd rect (at 6.35 6 ${p.r}) (size 2 2) (layers "${p.side}.Cu" "${p.side}.Paste" "${p.side}.Mask") (thermal_bridge_angle 45))
)
    `;
  },
};

