# GTA 6 took 13 years — my AI agent got paid instead — gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/sakasaki919-cmd/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/sakasaki919-cmd/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

Entry for the [make.fun](https://make.fun) bounty
[gta6-meme-x-01](https://make.fun/bounty/gta6-meme-x-01) — "Post a GTA 6 meme on X".
The post itself is the entry: the house reads it from X and an AI judge compares
the posts two at a time; the top 50 share $500.

## The meme

![meme](meme.png)

A Vice City sunset, thirteen years in the making. The joke is the wait: GTA V came
out in 2013 and GTA 6 only lands in 2026 — while the rest of us waited, my AI
agent went and earned real money on make.fun instead. The picture shows make.fun's
own ghost mascot (the real mark from the [press kit](https://make.fun/press/),
mark-1024.png) front and centre, with the caption drawn in large letters so it
reads even shrunk to 480×480.

The post's text (in `post-text.txt`) carries `@makefunai`, the bounty link and my
play code `makefun-sand-corn-ice`.

## The entry program

`main.ts` (Node 22, standard library only) copies `POST.json` — the posted X
post's address — from the repository root to the output directory, where the gate
reads it. It also refuses a placeholder or malformed address before copying, so a
bad `POST.json` fails loudly instead of entering an invalid entry.

Run it locally:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

`out/POST.json` is then byte for byte this directory's `POST.json`.

## The post

`POST.json` holds the post's address:

    {"url": "https://x.com/<handle>/status/<id>"}

Replace the placeholder with the real post's address once it is posted on X. Keep
the post up and the account public until the results are out.

make.fun is a site where people and their AI agents build things, enter them in
paid competitions (bounties) and earn real money when they win.
