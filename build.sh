#!/bin/sh
set -eu
container_cmd=docker
# Ensure we switch to the /board working directory, pointing it
# at the repo root (when running the script from there)
container_args="-w /board -v $(pwd):/board --rm"

# Define the boards to autoroute and export, and the plates
boards="knuckles_wireless"
plates="backplate frontplate controller_overlay"

# Define the pinned KiCad Auto Docker image to use
kicad_auto_image="ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65"

# Preserve manually routed files
if [ -e pcbs/*_manually_routed.kicad_pcb ]; then
    mkdir ergogen/tmp
    mv pcbs/*_manually_routed* ergogen/tmp
fi

# Cleanup the output folder or KiCad will error out
rm -rf outlines
rm -rf pcbs
rm -rf points
rm -rf source
rm -f cases/knuckles_bottom_tray.jscad cases/knuckles_bottom_tray.stl

# Cleanup Freerouting log outpus
if [ -e freerouting/freerouting.log ]; then
    rm freerouting/freerouting.log
fi
if [ -e logs/freerouting.log ]; then
    rm logs/freerouting.log
fi

# Generate unrouted PCBs with Ergogen (definition in package.json)
npm run debug

# Restore manually routed files
if [ -e ergogen/tmp/*_manually_routed.kicad_pcb ]; then
    mv ergogen/tmp/*_manually_routed* pcbs 
    rm -r ergogen/tmp
fi

for plate in ${plates}
do
    echo "\n\n>>>>>> Processing $plate <<<<<<\n\n"
    ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${plate}.kicad_pcb -c kibot/default.kibot.yaml
done

for board in ${boards}
do
    echo "\n\n>>>>>> Processing $board <<<<<<\n\n"
    if [ -e pcbs/${board}_manually_routed.kicad_pcb ]; then
        ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${board}_manually_routed.kicad_pcb -c kibot/boards.kibot.yaml
    fi
    if [ -e pcbs/${board}.kicad_pcb ]; then
        ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${board}.kicad_pcb -c kibot/default.kibot.yaml
        ./scripts/autoroute.sh "${board}"
    fi
    if [ -e pcbs/${board}_autorouted.kicad_pcb ]; then
        ${container_cmd} run ${container_args} ${kicad_auto_image} kibot -b pcbs/${board}_autorouted.kicad_pcb -c kibot/boards.kibot.yaml
    fi
done

# Docker runs as root and causes issues with file ownership
sudo chown -R "$USER" ergogen
sudo chown -R "$USER" freerouting
