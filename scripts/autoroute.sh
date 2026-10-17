#!/usr/bin/env bash

set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
board="${1:-knuckles_wireless}"
attempt_limit="${AUTOROUTE_ATTEMPTS:-3}"
platform="linux/amd64"

kicad_image="ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65"
router_image="knuckles-freerouting:2.1.0"

board_file="${root_dir}/pcbs/${board}.kicad_pcb"
project_file="${root_dir}/kicad/projects/${board}.kicad_pro"
rules_file="${root_dir}/freerouting/freerouting.rules"
output_file="${root_dir}/pcbs/${board}_autorouted.kicad_pcb"
output_project="${root_dir}/pcbs/${board}_autorouted.kicad_pro"
artifact_dir="${root_dir}/pcbs/autoroute/${board}"

if [[ ! -f "${board_file}" ]]; then
  echo "Board not found: ${board_file}" >&2
  exit 2
fi

if [[ ! -f "${project_file}" ]]; then
  echo "Canonical KiCad project not found: ${project_file}" >&2
  exit 2
fi

if [[ ! -f "${rules_file}" ]]; then
  echo "Freerouting rules not found: ${rules_file}" >&2
  exit 2
fi

if [[ ! "${attempt_limit}" =~ ^[1-9][0-9]*$ ]]; then
  echo "AUTOROUTE_ATTEMPTS must be a positive integer" >&2
  exit 2
fi

command -v docker >/dev/null 2>&1 || {
  echo "Docker is required to autoroute the board" >&2
  exit 2
}

work_dir="$(mktemp -d "${TMPDIR:-/tmp}/knuckles-autoroute.XXXXXX")"
trap 'rm -rf "${work_dir}"' EXIT

run_kicad() {
  docker run --rm \
    --platform "${platform}" \
    --volume "${root_dir}:/board:ro" \
    --volume "${work_dir}:/work" \
    --workdir /board \
    "${kicad_image}" \
    "$@"
}

echo "Building pinned Freerouting 2.1.0 image"
docker build \
  --platform "${platform}" \
  --tag "${router_image}" \
  "${root_dir}/docker/freerouting"

echo "Exporting ${board} with the pinned KiCad 8 toolchain"
run_kicad python3 kibot/export_dsn.py \
  -b "pcbs/${board}.kicad_pcb" \
  -o "/work/${board}.dsn"

best_attempt=""
best_score=""

for attempt in $(seq 1 "${attempt_limit}"); do
  attempt_dir="${work_dir}/attempt-${attempt}"
  mkdir -p "${attempt_dir}"
  cp "${work_dir}/${board}.dsn" "${attempt_dir}/${board}.dsn"

  echo "Routing attempt ${attempt}/${attempt_limit}"
  if ! docker run --rm \
      --platform "${platform}" \
      --volume "${root_dir}/freerouting:/rules:ro" \
      --volume "${attempt_dir}:/work" \
      "${router_image}" \
      -de "/work/${board}.dsn" \
      -do "/work/${board}.ses" \
      -dr /rules/freerouting.rules \
      -mp 25 \
      -mt 1 \
      -dct 0 \
      --gui.enabled=false \
      --profile.email=knuckles@localhost.invalid \
      >"${attempt_dir}/freerouting.log" 2>&1; then
    echo "Attempt ${attempt} failed in Freerouting" >&2
    continue
  fi

  if [[ ! -s "${attempt_dir}/${board}.ses" ]]; then
    echo "Attempt ${attempt} did not produce an SES file" >&2
    continue
  fi

  if ! run_kicad python3 kibot/import_ses.py \
      -b "pcbs/${board}.kicad_pcb" \
      -s "/work/attempt-${attempt}/${board}.ses" \
      -o "/work/attempt-${attempt}/${board}_routed_raw.kicad_pcb"; then
    echo "Attempt ${attempt} failed while importing its SES file" >&2
    continue
  fi

  cleanup_input="${board}_routed_raw.kicad_pcb"
  : >"${attempt_dir}/cleanup.log"

  for cleanup_pass in $(seq 1 10); do
    cleanup_output="${board}_cleanup_${cleanup_pass}.kicad_pcb"
    echo "cleanup_pass=${cleanup_pass}" >>"${attempt_dir}/cleanup.log"
    run_kicad python3 kibot/remove_dangling_tracks.py \
      "/work/attempt-${attempt}/${cleanup_input}" \
      "/work/attempt-${attempt}/${cleanup_output}" \
      2>&1 \
      | sed '/^swig\/python detected a memory leak/d' \
      >>"${attempt_dir}/cleanup.log"

    removed_tracks="$(grep '^removed_tracks=' "${attempt_dir}/cleanup.log" | tail -1 | cut -d= -f2)"
    cleanup_input="${cleanup_output}"

    if [[ "${removed_tracks}" -eq 0 ]]; then
      break
    fi
  done

  cp "${attempt_dir}/${cleanup_input}" \
    "${attempt_dir}/${board}_autorouted.kicad_pcb"

  cp "${project_file}" \
    "${attempt_dir}/${board}_autorouted.kicad_pro"

  run_kicad kicad-cli pcb drc \
    --output "/work/attempt-${attempt}/drc.rpt" \
    "/work/attempt-${attempt}/${board}_autorouted.kicad_pcb" \
    >"${attempt_dir}/drc.log" 2>&1

  run_kicad kicad-cli pcb drc \
    --format json \
    --output "/work/attempt-${attempt}/drc.json" \
    "/work/attempt-${attempt}/${board}_autorouted.kicad_pcb" \
    >>"${attempt_dir}/drc.log" 2>&1

  run_kicad python3 kibot/drc_metrics.py \
    "/work/attempt-${attempt}/drc.json" \
    >"${attempt_dir}/metrics.txt"

  unconnected="$(grep '^unconnected=' "${attempt_dir}/metrics.txt" | cut -d= -f2)"
  dangling="$(grep '^dangling=' "${attempt_dir}/metrics.txt" | cut -d= -f2)"
  errors="$(grep '^errors=' "${attempt_dir}/metrics.txt" | cut -d= -f2)"
  violations="$(grep '^violations=' "${attempt_dir}/metrics.txt" | cut -d= -f2)"
  score=$((unconnected * 1000000 + errors * 10000 + dangling * 100 + violations))

  cat >>"${attempt_dir}/metrics.txt" <<EOF
attempt=${attempt}
score=${score}
EOF

  echo "Attempt ${attempt}: ${unconnected} unconnected, ${dangling} dangling, ${errors} errors"

  if [[ -z "${best_score}" || "${score}" -lt "${best_score}" ]]; then
    best_attempt="${attempt}"
    best_score="${score}"
  fi

  if [[ "${unconnected}" -eq 0 && "${dangling}" -eq 0 && "${errors}" -eq 0 ]]; then
    break
  fi
done

rm -rf "${artifact_dir}"
mkdir -p "${artifact_dir}"

if [[ -z "${best_attempt}" ]]; then
  cp -R "${work_dir}"/attempt-* "${artifact_dir}/" 2>/dev/null || true
  echo "No routing attempt produced an importable result" >&2
  exit 1
fi

selected_dir="${work_dir}/attempt-${best_attempt}"
cp "${work_dir}/${board}.dsn" "${artifact_dir}/${board}.dsn"
cp "${selected_dir}/${board}.ses" "${artifact_dir}/${board}.ses"
cp "${selected_dir}/freerouting.log" "${artifact_dir}/freerouting.log"
cp "${selected_dir}/cleanup.log" "${artifact_dir}/cleanup.log"
cp "${selected_dir}/drc.log" "${artifact_dir}/drc.log"
cp "${selected_dir}/drc.rpt" "${artifact_dir}/drc.rpt"
cp "${selected_dir}/drc.json" "${artifact_dir}/drc.json"
cp "${selected_dir}/metrics.txt" "${artifact_dir}/metrics.txt"

selected_unconnected="$(grep '^unconnected=' "${selected_dir}/metrics.txt" | cut -d= -f2)"
selected_dangling="$(grep '^dangling=' "${selected_dir}/metrics.txt" | cut -d= -f2)"
selected_errors="$(grep '^errors=' "${selected_dir}/metrics.txt" | cut -d= -f2)"

if [[ "${selected_unconnected}" -ne 0 || "${selected_dangling}" -ne 0 || "${selected_errors}" -ne 0 ]]; then
  echo "No clean route found after ${attempt_limit} attempts" >&2
  echo "Best attempt: ${best_attempt}; see ${artifact_dir}" >&2
  exit 1
fi

cp "${selected_dir}/${board}_autorouted.kicad_pcb" "${output_file}"
cp "${project_file}" "${output_project}"

echo "Selected routing attempt ${best_attempt}"
echo "Routed board: ${output_file}"
echo "Routing evidence: ${artifact_dir}"
