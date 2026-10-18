# Knuckles artwork

Knuckles-inspired fan artwork for the wireless PCB: a stylized echidna badge,
forward-slanted wordmark, and paired speed stripes around the revision label.

- `concept.png`: original concept from the built-in image-generation tool.
- `badge.svg`: simplified single-color badge, placed at 12.5 mm nominal width.
- `wordmark.svg`: 22 mm nominal wordmark with speed stripes.
- `pcb-front.svg` / `pcb-back.svg`: actual silkscreen, mask openings, and board
  outline exported from KiCad. The back preview is viewed from the back.
- `pcb-render.png`: KiCad top-view render of the updated PCB.
- `pcb-18.5-render.png`: KiCad top-view render of the compact spacing option.

The wireless board places the badge between the battery connector and thumb
keys. The larger wordmark occupies the lower edge below the ring-finger column.
Both appear on F.SilkS and B.SilkS; back artwork is mirrored in board coordinates
so the lettering reads correctly from either assembled side. Filled polygons
print as one ink color. There are no added pads, copper, or mask openings.

The editable placement is in `ergogen/config.yaml`. The generated Ergogen
footprint is `ergogen/footprints/knuckles_artwork.js`. Normal board builds consume
that footprint directly and do not require Python or image generation.

To retrace the saved concept and regenerate the SVGs and footprint:

```sh
uv run scripts/build-knuckles-artwork.py
```

The tracing script uses a source-specific separation between the emblem and
wordmark, simplifies contours, removes tiny islands and highlights, and rounds
narrow tips for small-scale printing. Changing the source image requires
reviewing that separation and checking the final artwork at its physical size.

## Validation

Generated the wireless PCB with Ergogen 4.1.0 and loaded it with the pinned
KiCad 8 toolchain. Compared with base commit `4ea2e15`:

- All pre-existing electrical geometry and the board outline are identical.
- Changes are limited to two artwork footprints, the existing revision text,
  and the generated title-block date.
- KiCad 8 DRC reports the same 175 violations and 179 unconnected items before
  and after: 108 colocated-hole reports, 65 library warnings, and two pre-existing
  silkscreen/mask clipping warnings. No added artwork violations.
- Inspected both front and mirrored back exports for orientation and placement.

This is the generated **unrouted** board, not a refreshed manufacturing package.
The routed board and Gerbers must be regenerated through the usual pipeline
before fabrication. The older `ergogen/output/pcbs/` snapshots were left alone;
the current updated board is `pcbs/knuckles_wireless.kicad_pcb`.

## Spacing variants

`npm run build -- --spacing 18.5` and `--spacing 19.5` share these assets. The
compact board moves the badge up and left, and moves the wordmark/revision up,
to clear its mounting hole, thumb-key outline, and board edge. The default
19.5 mm artwork placement stays the same. See the repository README for separate
output folders and full routing/export commands.

KiCad 8 also checked the 18.5 mm generated board against an otherwise identical
control with the two artwork footprints removed. Both report the same 193
findings (108 colocated holes, 65 library warnings, and 20 existing mask-clipping
warnings) and 179 unconnected items. No artwork collisions remain. These are
checks on unrouted boards; both spacing options still need routing and the
manufacturing gate before ordering.

Footprint polygons follow the [KiCad S-expression format](https://dev-docs.kicad.org/en/file-formats/sexpr-intro/).
