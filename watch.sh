#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"

npm run debug -- --output ergogen/output "$@"
killall pcbnew || true
sleep 1
open ergogen/output/pcbs/knuckles_wireless.kicad_pcb

fswatch -o ergogen/config.yaml ergogen/footprints | while read f; do
  echo "Generating PCB..."
  npm run debug -- --output ergogen/output "$@"
  killall pcbnew || true
  sleep 1
  open ergogen/output/pcbs/knuckles_wireless.kicad_pcb
done
# watchexec --exts yaml -- 'ergogen . && open output/pcbs/left.kicad_pcb'


