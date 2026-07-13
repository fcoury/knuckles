import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const projects = ["knuckles_wireless.kicad_pro"];

await mkdir(resolve(root, "pcbs"), { recursive: true });

for (const project of projects) {
  await copyFile(
    resolve(root, "kicad", "projects", project),
    resolve(root, "pcbs", project),
  );
  console.log(`Synced KiCad project settings for ${project}`);
}
