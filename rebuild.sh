#!/bin/sh
container_cmd=docker
# Ensure we switch to the /board working directory, pointing it
# at the repo root (when running the script from there)
container_args="-w /board -v $(pwd):/board --rm"

# Define the boards to autoroute and export, and the plates
boards="knuckles_wireless"
kicad_auto_image="ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65"

# Cleanup Freerouting log outpus
if [ -e freerouting/freerouting.log ]; then
    rm freerouting/freerouting.log
fi
if [ -e logs/freerouting.log ]; then
    rm logs/freerouting.log
fi

for board in ${boards}
do
    echo "\n\n>>>>>> Processing $board <<<<<<\n\n"

    if [ -e pcbs/${board}.kicad_pcb ]; then
        ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${board}.kicad_pcb -c kibot/default.kibot.yaml
        ./scripts/autoroute.sh "${board}"
    fi
    if [ -e pcbs/${board}_autorouted.kicad_pcb ]; then
        ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${board}_autorouted.kicad_pcb -c kibot/boards.kibot.yaml
    fi
done

# Docker runs as root and causes issues with file ownership
sudo chown $USER -R ergogen
sudo chown $USER -R freerouting
