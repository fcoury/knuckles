# Knuckles

An open-source, column-staggered ergonomic keyboard. This repo contains everything to generate the PCBs, plates, renders/gerbers, and a simple printable bottom case tray.

![Knuckles with Case](images/photo.png)

It includes two PCB variants defined in `ergogen/config.yaml`:

- `knuckles`: wired variant (TRRS, small display)
- `knuckles_wireless`: wireless-ready variant (power switch, battery connector, e-paper display)

Both variants use reversible footprints and support per-key LEDs (SK6812mini-E) plus a small underglow chain. FR4 front/back plates and a controller overlay are also generated.

**Images**

- Front plate: `images/frontplate-top.png`, `images/frontplate-bottom.png`
- Back plate: `images/backplate-top.png`, `images/backplate-bottom.png`
- Controller overlay: `images/controller_overlay-top.png`, `images/controller_overlay-bottom.png`

## Requirements

- Node.js 18+ (CI uses Node 20)
- Docker (for the KiCad/KiBot/Freerouting pipeline in the shell scripts)
- Git with submodules (footprints are vendored as a submodule)
- Optional: macOS `fswatch` for `watch.sh` live-regeneration

Clone with submodules:

```
git clone --recursive <repo-url>
```

Install JS deps:

```
npm install
```

## Quick Start

There are two ways to build, depending on how much automation you want.

- Ergogen-only (local, fast):
  - `npm run build` → generates PCBs/plates from `ergogen/config.yaml` and the case STL.
  - `npm run debug` → same as build but with Ergogen debug output.
  - `npm run watch:build` / `npm run watch:debug` → rebuild on YAML/JS changes.

- Full pipeline (Docker, KiCad + Freerouting):
  - `./build.sh` →
    - Cleans previous outputs
    - Runs Ergogen (unrouted boards + plates)
    - Runs KiBot to export renders/gerbers for plates and unrouted board
    - Exports DSN, autoroutes with Freerouting, imports SES back into KiCad
    - Runs KiBot again for the autorouted board
    - Outputs live in `pcbs/`, `outlines/`, `ergogen/output/images`, `ergogen/output/gerbers`
  - `./rebuild.sh` → re-export/autoroute existing boards in `pcbs/` without regenerating from Ergogen.
  - `./watch.sh` (macOS) → regenerates PCB on config change and opens the result.

Notes:

- If case STL generation fails, check the path in `package.json` (`cases/knuckles_bottom_tray.jscad`) vs the file in `cases/`.
- Shell scripts expect Docker to be available and will pull/use containers automatically.

## Outputs

- `pcbs/` — KiCad 8 `.kicad_pcb` files for boards and plates.
- `outlines/` — DXF/SVG outlines used by the PCBs and case.
- `cases/` — JSCAD source and generated STL for a bottom tray.
- `ergogen/output/images` — board renders (from KiBot/PCBDraw).
- `ergogen/output/gerbers/<board>` — JLCPCB-ready Gerbers and drills (zipped by KiBot).
- `images/` — reference renders checked into the repo.

## Customizing

Edit `ergogen/config.yaml`:

- Layout: matrix and thumb-fan are under `points.zones.*` (spacing, splay, stagger).
- Switch footprint: set `meta.footprint` and optionally switch `presets` (`mx`, `choc_v1`, `choc_v2`, or the provided low-profile/reversible footprints).
- Electrical nets: column/row nets are assigned per zone; MCU pins are mapped in the `mcu` footprint section.
- LEDs: per‑key and underglow chains can be tweaked (trace widths, via sizes, positions).
- Case: see `cases/` and the outlines under `outlines/_bottom_case*` to adapt walls and cutouts.

After changes, rebuild via Ergogen (`npm run build`) or run the full pipeline (`./build.sh`).

## CI

A GitHub Actions workflow (`.github/workflows/build.yaml`) reproduces the full pipeline in containers:

- Ergogen generation
- KiBot renders + Gerbers (plates and board)
- DSN export → Freerouting autoroute → SES import
- Artifacts: `cases`, `gerbers`, `images`, `outlines`, `pcbs`

## Manufacturing

Use the KiBot-produced ZIP under `ergogen/output/gerbers/<board>` for JLCPCB. The KiBot configs (`kibot/default.kibot.yaml`, `kibot/boards.kibot.yaml`) are tuned for JLCPCB and include common filters for autorouted boards.

## Folder Structure (high level)

- `ergogen/` — main Ergogen project (`config.yaml`, footprints, generated output)
- `pcbs/` — KiCad boards (unrouted and autorouted variants)
- `kibot/` — KiBot configs and helper scripts (DSN export / SES import)
- `freerouting/` — rules, JARs, and logging for autorouting
- `cases/` — JSCAD for the printed bottom tray
- `images/` — reference images of plates
- `build.sh`, `rebuild.sh`, `watch.sh` — automation scripts

## License

MIT © 2024 Felipe Coury (see `LICENSE`).

## Credits

- Ergogen 4 and community for the generation engine.
- Custom footprints from `ergogen/footprints/ceoloide` (submodule) and related authors.
- Freerouting for autorouting; KiBot + PCBDraw for renders/exports.
