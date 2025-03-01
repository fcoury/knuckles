#!/bin/bash

# set -euo pipefail

cd ergogen

ergogen --clean .
killall pcbnew || true
sleep 1
open output/pcbs/zeph_wireless.kicad_pcb

fswatch -o config.yaml | while read f; do
  echo "Generating PCB..."
  ergogen --clean .
  killall pcbnew || true
  sleep 1
  open output/pcbs/zeph_wireless.kicad_pcb
done
# watchexec --exts yaml -- 'ergogen . && open output/pcbs/left.kicad_pcb'


