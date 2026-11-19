// gta6-meme-x-01 entry (Node 22, standard library only).
//
// The entry is the X post itself: a GTA 6 meme made by this agent, posted from a
// public X account with make.fun (a link or written out) and/or a tag of @makefunai
// and the entrant's play code in its text. This program only hands the post's
// address to the house: it copies POST.json from the repository root to the
// output directory, where the gate reads it. Nothing else it writes is judged.
//
// Local run (the grader sets /bot and /output; these env vars stand in for them):
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const repoDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const postFile = join(repoDir, "POST.json");

if (!existsSync(postFile)) {
  console.error(`POST.json not found in ${repoDir}`);
  process.exit(1);
}

// Refuse a placeholder or malformed address before copying, so a bad POST.json
// fails loudly here instead of passing an invalid entry to the gate.
const parsed: unknown = JSON.parse(readFileSync(postFile, "utf8"));
const url = (parsed as { url?: unknown } | null)?.url;
if (typeof parsed !== "object" || parsed === null || typeof url !== "string" ||
    !/^https:\/\/(x\.com|twitter\.com)\//.test(url)) {
  console.error(`POST.json does not name an X post address: ${JSON.stringify(parsed)}`);
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(postFile, join(outDir, "POST.json"));
