# Integrated-board firmware checkpoint

These are development builds for the new integrated circuit, not nice!nano
replacement images. Nothing has been flashed. Charging is disabled by default.

The board package targets the existing ZMK v0.3.0 / Zephyr 3.5 configuration.
Both halves build and produce UF2 images at **0x26000**. The custom Adafruit
bootloader uses **S140 6.1.1**, with the bootloader at 0xF4000 and storage reserved
at 0xEC000–0xF3FFF. Do not substitute a different SoftDevice version without
reviewing the application offset and partitions.

The existing working Knuckles shields and keymap were copied from
`fcoury/zmk-config` commit `abe5c7cbc6e37160c0a2e482b239e15af5ac9588`.
The IQS5xx driver is pinned at `e19e55deaf8eeb0d32d9c2fe17e3f87f5287a5a5` with
the previously validated polling wake/retry patch retained in `patches/`.
Only the integrated board enables the new power policy.

## Reproduce the build

The builder uses pinned container/toolchain and source revisions. It checks the
source checkout, applies the retained IQS5xx patch only to a pristine driver,
builds both hands, builds the custom bootloader, and checks UF2 address ranges,
family IDs, split roles, USB power, RC clock and disabled charging. It never
flashes hardware. Generated images are ignored by Git; their hashes are kept in
[build-verification.json](build-verification.json).

For the existing local workspaces, from the keyboard repository root:

```sh
python3 -B hardware/integrated-controller/firmware/build.py \
  --workspace /Users/fcoury/.cache/knuckles-firmware-build \
  --bootloader /Users/fcoury/.cache/knuckles-bootloader
```

For a new workspace, use the standard west workflow with `config/west.yml`:
copy this `config/` directory into a dedicated workspace, run `west init -l
config` there, then `west update`. ZMK must resolve to
`edf5c0814fd3ea202e43aad2d68fd32e882a518c` and Zephyr to
`dacab4875df72109b96cc8977547a0dc04875bcd`; the builder checks those revisions.
Clone `https://github.com/adafruit/Adafruit_nRF52_Bootloader` at tag `0.9.2`
(`eefbe6bda98b80cb296e2f1bb1c982d58fe4c12d`) and initialize its submodules.
Pass the two resulting paths to `build.py`. The build adds only this board's
files to the bootloader checkout and uses distinct west build directories.

The bootloader uses private-test USB ID **1209:0001**, per
[pid.codes' restrictions](https://pid.codes/1209/0001/). It is not a unique
product identifier and must be replaced with an appropriate allocation before
manufacture/distribution. ZMK application builds retain the upstream ZMK IDs.

## Power behavior and tests

`src/charge_policy.c` contains the register policy; `src/power.c` connects it to
Zephyr GPIO/I2C, USB events and the charger interrupt. The PMIC bus is dedicated,
so touchpad polling cannot directly contend for the charger I2C peripheral.
A timer schedules health reads every 30 s without periodically rewriting the
charge configuration. USB/PMIC events schedule an immediate service pass.

Run the focused host regression tests from the repository root:

```sh
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined \
  hardware/integrated-controller/firmware/src/charge_policy.c \
  hardware/integrated-controller/firmware/tests/charge_policy_test.c \
  -o /tmp/knuckles-charge-test
/tmp/knuckles-charge-test
```

They cover all three current profiles, unverified packs, unknown profiles,
incorrect device ID, write/readback and I2C failures, unexpected register reset,
no charge-cycle restarts from polling, open NTC, missing VIN power-good, fault
latching across suspend/resume, GPIO-disable failure fallback and empty-battery
suspend shutdown. The simulated register device does not validate analog
behavior or real-time USB deadlines.

`CONFIG_KNUCKLES_BATTERY_VERIFIED` remains off. Battery profile 110/20 mA is
the default; 250/50 mA and 500/100 mA are explicit Kconfig choices. Changing a
profile is a build-time decision, not automatic capacity detection. Enabling
charging also requires fitting R12 after the cell and thermistor are verified.
Use a separate test build/config when bring-up reaches that stage; the default
builder intentionally asserts that charging is disabled.

Both mechanical switches must remain on for firmware-supervised charging.
The left half enumerates CDC for host power authorization; keys still travel
through the right central. The prototype requires a USB host to charge; wall
chargers that never enumerate are not supported. Deep system-off sleep is
disabled while the initial watchdog policy is in use. See
[ENGINEERING.md](../ENGINEERING.md) for the complete power contract.

## First programming and verification

A new module needs initial programming over **SWD**. J5 exposes VTREF, SWDIO,
GND, SWCLK, RESET and GND on six 0.9 mm pads at 1.27 mm pitch. It needs a custom
pogo fixture; it is not mechanically compatible with a Tag-Connect cable.
VTREF senses target voltage and is not an external power input.

Program the merged bootloader/S140 HEX using a 3.3 V-compatible SWD probe after
power-rail checks. Then use the KNUCKLES UF2 volume to load the appropriate
half. These are bring-up instructions, not a record of successful programming.
Keep R12 open throughout initial tests.

The bootloader uses internal LF RC, enables only normal-voltage REG1 DC/DC,
holds charge enable low, disables an inherited PMIC watchdog and limits input
to 100 mA. On host suspend it switches SYS off; reconnect USB to recover.
Its bounded TWI writes and suspend behavior need verification on the actual
PMIC. Double-tap reset, interrupted UF2 recovery, USB sleep/wake and SWD recovery
are explicit bench acceptance tests.
