import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdir, mkdtemp, readFile, realpath, rm, symlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import yaml from "js-yaml";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const script = join(root, "scripts/build.mjs");

test("build both spacings without editing the source configuration", async t => {
  const temp = await mkdtemp(join(tmpdir(), "knuckles-spacing-test-"));
  t.after(() => rm(temp, { recursive: true, force: true }));
  const source = await readFile(join(root, "ergogen/config.yaml"), "utf8");
  // Exercise symlinked output paths (including macOS /tmp -> /private/tmp).
  await mkdir(join(temp, "outputs"));
  await symlink(join(temp, "outputs"), join(temp, "shortcut"), "dir");
  for (const spacing of [18.5, 19.5]) {
    const output = join(temp, "shortcut", String(spacing));
    // Exercise explicit CLI selection (including precedence) and env selection.
    const args = [script, "--debug", "--output", output];
    if (spacing === 18.5) args.push("--spacing", String(spacing));
    const result = spawnSync(process.execPath, args, {
      cwd: root, encoding: "utf8", env: { ...process.env, KNUCKLES_SPACING: "19.5" },
    });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    const points = yaml.safeLoad(await readFile(join(output, "points/points.yaml"), "utf8"));
    assert.equal(points.matrix_pinky_bottom.x - points.matrix_outer_bottom.x, spacing);
    assert.equal(points.matrix_outer_home.y - points.matrix_outer_bottom.y, spacing);
    for (const name of ["knuckles", "knuckles_wireless", "frontplate", "backplate", "controller_overlay"]) {
      assert.match(await readFile(join(output, `pcbs/${name}.kicad_pcb`), "utf8"), /^\s*\(kicad_pcb/);
    }
    const board = await readFile(join(output, "pcbs/knuckles_wireless.kicad_pcb"), "utf8");
    assert.match(board, /knuckles_artwork_badge/);
    assert.match(board, /knuckles_artwork_wordmark/);
    const model = board.match(/\(model "\$\{KIPRJMOD\}\/([^"]+)"/)[1];
    assert.equal(await realpath(resolve(await realpath(join(output, "pcbs")), model)), await realpath(join(root, "models/PG1316S.step")));
    assert.match(await readFile(join(output, "cases/knuckles_bottom_tray.stl"), "utf8"), /facet normal/);
    assert.deepEqual(JSON.parse(await readFile(join(output, "pcbs/build-info.json"), "utf8")), { spacing_mm: spacing });
    assert.equal(await readFile(join(output, "pcbs/knuckles_wireless.kicad_pro"), "utf8"), await readFile(join(root, "kicad/projects/knuckles_wireless.kicad_pro"), "utf8"));
  }
  assert.equal(await readFile(join(root, "ergogen/config.yaml"), "utf8"), source);
});

test("reject unsupported spacing before writing outputs", async t => {
  const output = await mkdtemp(join(tmpdir(), "knuckles-invalid-spacing-"));
  t.after(() => rm(output, { recursive: true, force: true }));
  await writeFile(join(output, "sentinel"), "keep");
  const result = spawnSync(process.execPath, [script, "--spacing", "17", "--output", output], { encoding: "utf8" });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Unsupported spacing/);
  assert.equal(await readFile(join(output, "sentinel"), "utf8"), "keep");
});
