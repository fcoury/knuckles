# Integration validation — 2026-10-18

The integrated-controller branch was merged with main at `24febbc`. The README
conflict was resolved by retaining the current documentation, artwork and
ordered-board archive, with a link to the opt-in integrated prototype.
The normal nice!nano PCB and 18.5 mm default are unchanged.

Validation completed on the integrated tree:

- `npm test`: all three build tests passed, covering both spacings.
- `npm run build:integrated`, with default 18.5 and explicit 19.5 mm: passed.
- `npm run check:integrated`: passed physical/ERC and electrical/matrix checks.
  Partial source boards still have unrouted connections, as documented.
- `npm run check:integrated:routed`: all four retained native layouts passed;
  zero physical errors and zero airwires. Existing warning counts are 27/22
  (18.5 mm left/right) and 12/13 (19.5 mm left/right).
- The routed checks were repeated against the retained source snapshots after
  excluding generated UUID/timestamp churn from this integration.
- The integrated firmware builder rebuilt both halves and the custom bootloader;
  partition, GPIO, split-role and disabled-charging assertions passed.
- Host charge-policy regression tests passed with address/undefined-behavior
  sanitizers and `-Wall -Wextra -Werror`.

Only the mouse-button keymap was synchronized from zmk-config `e2d5f00`.
The existing TPS43 polling wake patch already matched. Integrated pin mapping,
power policy, bootloader and disabled charging were preserved. Its firmware
remains hardware-untested; the nice!nano pair's successful mouse-button check
is not validation of this new circuit.

No integrated board was flashed or ordered. Sourcing, DFM, mechanical clearance,
USB product identification and bench validation remain the release gates in
[README.md](README.md). Rebuilding is not fabrication approval.
