import { spawnSync } from "node:child_process";
import { copyFile, mkdir, mkdtemp, readFile, realpath, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { parseArgs } from "node:util";
import yaml from "js-yaml";

const require = createRequire(import.meta.url);
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const { values } = parseArgs({
  options: {
    spacing: { type: "string", default: process.env.KNUCKLES_SPACING },
    output: { type: "string", default: "." },
    debug: { type: "boolean", default: false },
    help: { type: "boolean", default: false },
  },
});

if (values.help) {
  console.log("Usage: npm run build -- [--spacing 18.5|19.5] [--output DIR] [--debug]");
  console.log("Spacing defaults to KNUCKLES_SPACING or the pg1316s preset in ergogen/config.yaml.");
  process.exit(0);
}

const config = yaml.safeLoad(await readFile(join(root, "ergogen/config.yaml"), "utf8"));
const spacing = values.spacing ?? String(config.presets.pg1316s.ks);
if (!["18.5", "19.5"].includes(spacing)) {
  throw new Error(`Unsupported spacing '${spacing}'; choose 18.5 or 19.5 mm.`);
}
config.presets.pg1316s.ks = Number(spacing);
config.presets.pg1316s.kp = Number(spacing);
const output = resolve(root, values.output);
await mkdir(output, { recursive: true });

// Keep the existing 3D model reference valid in isolated output directories too.
config.pcbs._knuckles_baseline.footprints.key_switches_f.params.switch_3dmodel_filename =
  "${KIPRJMOD}/" + relative(join(await realpath(output), "pcbs"), await realpath(join(root, "models/PG1316S.step"))).split("\\").join("/");

function run(script, args) {
  const result = spawnSync(process.execPath, [script, ...args], { cwd: root, stdio: "inherit" });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${script} failed (${result.status ?? result.signal}).`);
}

const input = await mkdtemp(join(tmpdir(), "knuckles-build-"));
try {
  // Ergogen's folder input loads the same footprint bundle as a normal build.
  await writeFile(join(input, "config.json"), JSON.stringify(config));
  await symlink(join(root, "ergogen/footprints"), join(input, "footprints"), "dir");
  console.log(`Building Knuckles: ${spacing} mm spacing → ${output}`);
  run(require.resolve("ergogen/src/cli.js"), [input, "--output", output, ...(values.debug ? ["--debug"] : [])]);
  await copyFile(join(root, "kicad/projects/knuckles_wireless.kicad_pro"), join(output, "pcbs/knuckles_wireless.kicad_pro"));
  run(require.resolve("@jscad/cli/cli.js"), [join(output, "cases/knuckles_bottom_tray.jscad"), "-of", "stla", "-o", join(output, "cases/knuckles_bottom_tray.stl")]);
  await writeFile(join(output, "pcbs/build-info.json"), JSON.stringify({ spacing_mm: Number(spacing) }, null, 2) + "\n");
} finally {
  await rm(input, { recursive: true, force: true });
}
