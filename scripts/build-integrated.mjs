import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import yaml from 'js-yaml';

const root=resolve(dirname(fileURLToPath(import.meta.url)), '..');
const {values}=parseArgs({options:{spacing:{type:'string',default:process.env.KNUCKLES_SPACING??'18.5'}}});
if(!['18.5','19.5'].includes(values.spacing)) throw new Error('Choose 18.5 or 19.5 mm spacing.');
const hardware=join(root,'hardware/integrated-controller');
const image='ghcr.io/inti-cmnb/kicad8_auto@sha256:678b9c219ccaa36aa085af6b17015a67c97eef8f16c56c972a49007a63914a65';
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)throw new Error(`${cmd} failed (${r.status})`);}
const source=await mkdtemp(join(tmpdir(),'knuckles-integrated-'));
try {
  run(process.execPath,['scripts/build.mjs','--debug','--spacing',values.spacing,'--output',source]);
  const points=yaml.safeLoad(await readFile(join(source,'points/points.yaml'),'utf8'));
  const anchor=points.mcu_cover_top_left;
  await writeFile(join(source,'integration-anchors.json'),JSON.stringify({spacing_mm:Number(values.spacing),controller_origin:[anchor.x+.652,-anchor.y-.2275],mirror_axis_x:(points.matrix_outer_bottom.x+points.mcu_cover_top_right.x)/2}));
  run('python3',['-B',join(hardware,'generate.py')]);
  run('docker',['run','--rm','--platform','linux/amd64','-e','PYTHONDONTWRITEBYTECODE=1',
    '-v',`${root}:/repo`,'-v',`${source}:/source`, '-w','/repo/hardware/integrated-controller',image,
    'python3','integrate.py','--source','/source','--output',`output/integrated/${values.spacing}`]);
} finally { await rm(source,{recursive:true,force:true}); }
