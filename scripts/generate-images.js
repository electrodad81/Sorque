import 'dotenv/config';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import OpenAI from 'openai';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const STYLE_PREFIX =
  '1-bit black and white pixel art, high contrast, dithered, classic Macintosh adventure game style, no text:';

const WORLD_PATH = join(ROOT, 'public', 'worlds', 'escape_house_01.json');
const ROOMS_DIR = join(ROOT, 'public', 'images', 'rooms');
const DEATHS_DIR = join(ROOT, 'public', 'images', 'deaths');

// Death scenes to generate — keyed by cause, value is the scene description
const DEATH_SCENES = {
  dog: 'A large shadowy guard dog emerging from a dark basement corner, glowing eyes in darkness, menacing silhouette, concrete walls with shelves and paint cans, dramatic low angle',
  fall: 'A person falling into a deep dark pit, arms flailing, seen from above looking down into blackness',
  trap: 'A cruel iron bear trap snapping shut, sprung on a stone floor in a dim cellar',
  thorns: 'Dense thorny hedge walls closing in, sharp thorns dripping, a figure trapped and tangled in the branches',
  poison: 'A shattered glass vial on a stone floor, dark liquid pooling, swirling smoke rising, tunnel vision vignette effect, ominous atmosphere',
  generic: 'A figure collapsed on a stone floor in darkness, dramatic shadows, a single beam of light from above',
};

async function generateImage(openai, prompt, outPath, label) {
  if (existsSync(outPath)) {
    console.log(`[skip] ${label} — image already exists`);
    return;
  }

  console.log(`[gen]  ${label} — generating...`);

  try {
    const response = await openai.images.generate({
      model: 'dall-e-3',
      prompt: `${STYLE_PREFIX} ${prompt}`,
      n: 1,
      size: '1024x1024',
      quality: 'standard',
      response_format: 'b64_json',
    });

    const b64 = response.data[0].b64_json;
    writeFileSync(outPath, Buffer.from(b64, 'base64'));
    console.log(`[done] ${label} — saved ${outPath}`);
  } catch (err) {
    console.error(`[err]  ${label} — ${err.message}`);
  }
}

async function main() {
  if (!process.env.OPENAI_API_KEY) {
    console.error('Missing OPENAI_API_KEY in .env');
    process.exit(1);
  }

  const openai = new OpenAI();
  const world = JSON.parse(readFileSync(WORLD_PATH, 'utf-8'));
  const rooms = world.rooms;

  // Generate room images
  for (const [roomId, room] of Object.entries(rooms)) {
    const outPath = join(ROOMS_DIR, `${roomId}.png`);
    await generateImage(openai, room.desc_long, outPath, `Room ${roomId} (${room.name})`);
  }

  // Generate death scene images
  for (const [cause, description] of Object.entries(DEATH_SCENES)) {
    const outPath = join(DEATHS_DIR, `${cause}.png`);
    await generateImage(openai, description, outPath, `Death: ${cause}`);
  }

  console.log('\nAll done.');
}

main();
