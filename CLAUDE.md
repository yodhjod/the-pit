# The Pit

A mobile web game made for a group of friends. The player descends a giant pit that opened in the middle of their city, in the spirit of Made in Abyss. The friends appear in the game as characters, but none of them is the main player.

## Direction from the group

- Must run on both Android and iPhone in the browser, with no install. Touch first, keyboard as a fallback.
- Genres voted: adventure/RPG (Pokémon Black/White, X/Y era), hack 'n' slash, survival.
- Tone: sarcastic and parodic on the surface, genuinely dark underneath. The rim town is a tourist trap and the bureaucracy is absurd (delver permits, "NO REFUNDS" signs).
- The real city and its landmarks will anchor the setting. Not decided yet: which city, which places, the friends' names and looks.

## Game structure (planned)

A rhythm roguelike. The run is a descent through **chapters**, and each chapter is a run of **levels**.

- **Pace:** quick, addictive runs like most roguelikes. Dying ends the run and you start again from the top. Upgrades bought during a run last only for that run. (The Pokémon-style adventure/RPG direction from the group vote is set aside for now.)
- **Fixed levels, structured story:** the levels, their charts and their order are the same every run. The story is told in fixed snippets of lore along the way. The pull is curiosity: see what comes after the level where you last died, and find out what's at the bottom of the pit.
- **Mastery through death:** each death teaches the player the charts, so they get better and faster with practice, like learning a song.

- **Chapters** are each themed on something from the city. The levels in a chapter share that theme. The theme is mostly an art problem, so keep it generic in code for now.
- **Descent levels** are the core gameplay (what `index.html` prototypes). Each one is harder than the last, with its own music, so difficulty rises the deeper you go.
- **Vendor levels:** one or two per chapter. No descending: a calm area with a vendor who sells fun upgrades, and maybe lore or story, before you go on.
  - Stock varies per run (the levels don't), so runs differ in the build you put together.
  - Upgrades come in tiers. Stronger ones appear deeper and cost more. An expensive item may be on display early, out of reach by design, to tease what's coming.
  - Later, different vendor types take different currencies, in the spirit of The Binding of Isaac (shops for coins, devil deals paid in health). For example, a shady vendor deeper down who takes lanterns.
- **Boss level:** the last level of each chapter. You beat it to keep descending. Still rhythm-based, but not about walking down stairs. The gameplay is undecided.
- **Currency:** coins or points earned by playing well, spent at vendors on upgrades.

## Current focus: `index.html` (Pit Descent)

A small gameplay prototype of one chapter, in side view. The real game will be quite different; this file is for finding the feel of the core rhythm loop and the run structure.

- **The run** (`RUN`): Rim → Drowned Metro → vendor → Ossuary → Spore Gardens → vendor → Depths → boss. Each descent level plays one song (a music file, or the built-in 32-beat chart with procedural music), then a "Level cleared" screen with its fixed lore line. Lanterns and coins carry over between levels; losing all lanterns ends the run. The deepest node reached is saved in localStorage (`pitBest`) and shown on the title and death screens.
- **Coins:** Perfect = 2, Good = 1, plus upgrade bonuses.
- **Vendors** (`openVendor`, `UPG`): each vendor node lists how many items to roll per tier; stock is random per run, items already owned are skipped. Upgrades are flags in `G.up` checked where they apply (`score`, `loseHeart`, `fail`, `relight`), or change the timing windows `W_P`/`W_G`/`W_S` directly.
- **Boss** (`startBoss`, `BOSS_CHART`, `BOSSG`): the Inspector, a giant eye in a cap. The explorer stands still at the bottom camp. Same four actions: tap = strike, hold = charged strike, swipe up/down = dodge its low sweep / high swipe. Before a sweep the iris takes the cue colour and the eye winds up, then lunges on the beat. 40 HP, the 32-beat chart loops 3 times; if it runs out, the run ends. Placeholder for the boss design.

- **The world keeps the beat.** The explorer walks the ledge on their own at a steady pace (`SPEED` units per second); walking is not judged. Their position is a pure function of level time (see the hero section in `frame()`), so the visuals stay on the beat even when the player misses. The walk cycle is locked to the song's beats (a footfall per beat, every other beat above ~140 bpm).
- **The notes are things on the ledge.** A note at level time t sits at distance `SPEED·t` along the ledge, so the explorer reaches it on its beat. tap = whack a critter, swipe up = jump an obstacle or a missing step (`n.gap`), swipe down = duck a swooper, hold = ride a zipline over a chasm (let go on the landing). Input only changes the outcome: a whack or a bite, a jump or a bonk/fall, a duck or a bat hit, riding the line or dropping in.
- **The ledge** (`buildLevel`, `pathPt`) is built for each level from its chart and winds down the pit, more than one turn for long songs (at least `MINPITCH` drop per turn so turns never touch). Each layer has its own ledge look in `LSTYLE`: stairs (flat landings and short flights), planks, stone slabs, mushroom caps. Decor is built once at load, so `clearLedge` hides decor instances that poke into the current walkway, and a camera cutaway (`CUT`) dithers away decor right in front of the camera.
- **Layers:** Rim, Drowned Metro, Ossuary, Spore Gardens, Depths. Each has its own palette, decor, obstacle, critter colour, ledge look, move mix for generated charts (`LSTYLE[L].mix`, `gap`), and built-in music mode and BPM (88, 96, 100, 108, 84). The boss's built-in music runs at 112.
- **Stakes:** 5 lanterns (hearts). One is relit per new level.
- **Mistakes bend and slow the music** (`glitch`, `warp`): for half a second the music is muffled and crunched (both music files and procedural music go through a bus, `mkBus`, with a dry path and a distorted, filtered wet path). The song and the level also slow down together: each mistake adds a warp where level time runs at 1 − depth·sin²(πu), and a music file's playback rate follows the same curve, so they stay in sync (measured within ~3 ms). Wrong key: a music file gets clean copies of itself a semitone up and down (`GL.pitch`) laid over the crunch for the same half second, starting from where the song is and following the slowdown; the built-in music bends every note playing (tracked in `LIVE`) by `pitch[0]` semitones. Each mistake puts the level `slow·slowDur/2` s behind; stacked warps never go below quarter speed. All the knobs are in `GL`. Triggered next to `thud()` on every miss.
- **Feedback:** the rhythm track at the bottom is the main timing UI, with an early/late meter. There's also a ring under the finger, a fixed marker on the ledge where the next move happens, and a flash when its beat hits.
- **Explorer:** a rigged pixel-art sprite generated in code (`drawPose` and `POSES`). Its walk is a cartoon sneak (modelled on a classic sneak-cycle reference): hunched forward and low on tiptoe, arms swinging low and opposite to the legs like a march, hands dangling, swapping with each step (`armSwap`); the far leg and arm are drawn much darker so the alternation reads at small size. The knee lifts high before the beat, then a long toe-first stride lands on the beat. Poses are skeleton coordinates, so friends can be built later by swapping hat, hair, glasses and colours.

## Tech

- Single self-contained HTML file. No build step.
- Three.js r128 from cdnjs (UMD global `THREE`). Google Fonts: Cormorant Garamond and IBM Plex Mono.
- All art is procedural: low-poly toon-shaded geometry, instanced decor, canvas textures, pixel sprites drawn into canvases.
- Music: a level's music file plays straight to the speakers (`trackPlay`); otherwise procedural Web Audio (a pad, bass, arpeggio and kick per layer, generated per beat in `musicBeat`). Move sounds over a music file are short and unpitched (`sfx`).
- **Songs:** everything a level needs is a song object in level seconds (0 = level start): `beats`, `bar0`, `notes` (`at`, `type`, `len`, `gap`), `first`, `end`, plus `buf`/`from` for a music file or `proc`/`lead` for a built-in one. `procSong` builds one from a beat chart; `trackSong` from a generated chart.
- **Music files → levels:** `RUN` descent nodes take `track:'music/x.mp3'` (served over http, so not from `file://`), optional `from`/`to` seconds, and `diff` 0–1. On a load failure the built-in chart plays. The title screen's "Play your own song" analyses any file the player picks and builds one level (difficulty, whole song or best minute, which layer).
  - `analyse` (in-browser, ~0.3 s per 40 s of audio): spectral flux onsets in three bands (lows/kicks, mids/snares and voices, highs/hats), tempo by autocorrelation with a 120 bpm prior, beats by dynamic programming (Ellis 2007), then snapped to a fitted steady grid when the song keeps strict time (period and phase fine-tuned against the onset curve). Also finds the bar phase (heaviest kicks) and a per-beat loudness 0–1. On synthetic drum tracks (92–174 bpm, jittered, silent intro) it gets the tempo exact and beats within ~2 ms; `AN.lat` holds the measured frame-time offset.
  - `makeChart`: candidate slots on beats and half-beats (quarters at the top difficulty), a slot gets a note when the music has an accent there, picked two bars at a time with a note budget from difficulty × loudness, with a minimum gap. The band behind each accent picks the move (kicks → jumps, snares → critters, hats → swoopers), nudged towards the layer's mix. Then playability rules (room around swipes, no more than three identical swipes in a row), long quiet stretches become ziplines, and some jumps become missing steps. Deterministic: the same file always gives the same level.
- **Timing:**
  - `timeOf(levelSeconds)` maps level time to AudioContext time and `levelAt(T)` back (`anchorT` = level start, minus the lag from any warps). Never use `anchorT` directly. A music file has no scheduled end: the frame loop fades it out near the level's end.
  - `clock()` returns the *heard* time: it compensates output latency and is smoothed against `performance.now()`.
  - Inputs use the event's own `timeStamp` through `clockAt()`.
  - The audio delay offset (`offsetMs`) is user-set or measured with the Calibrate screen, and saved in localStorage.
- Built-in charts live in `CHART`: per layer, 32 beats of `[beat, type, holdBeats]`, with type `t`/`u`/`d`/`h`. The boss chart is `BOSS_CHART`, same format. `LV` is the level being played (`{L, song, path, nd}`) and `ACT` its notes being judged.

## Reading `index.html` cheaply

The file is ~125 KB of dense one-line code, so don't read it whole. Grep `/\* ----------` to list the sections with line numbers, then read only the range you need. Sections, in order: utils · chart · the run (`RUN`, `UPG`, boss chart) · world constants · lighting · pit wall · instancing · rim · the ledge (`buildLevel`, `pathPt`, `buildCamp`) · signs · obstacles/critters/swoopers · layers 0–4 decor · glow points · light shafts · particles · creatures · explorer (`drawPose`, `POSES`) · chapter boss (3D model) · sparkles · audio (`clock`, `musicBeat`, `trackPlay`, `sfx`) · music analysis (`analyse`) · level generator (`makeChart`, `bestWindow`, `loadTrack`) · action cues · game state (judging, `score`, `loseHeart`) · run flow (`newRun`, `songFor`, `startLevel`, `levelClear`, `openVendor`, `startBoss`, `fallOut`, `finish`, decor cutaway + `clearLedge`, your-own-song screen `CU`) · input + calibration · gauge · next-action marker + beat flashes · rhythm track (`drawTrack`) · frame loop (`frame`).

## Conventions

- Keep the game a single HTML file unless it grows past the point of being workable. Prefer small, surgical edits.
- Test in a headless Chromium (Playwright with `--use-gl=swiftshader`), or in the desktop app's browser pane via the `the-pit` server in `.claude/launch.json` (serves the folder on http://localhost:8123). Software rendering is slow, so judge visuals from screenshots, not timing accuracy. The pane's tools run in an isolated world: to reach the game's debug hook `window.__pit` (analyse, makeChart, playCustom, CU, LV, G, S, C), inject a `<script>` and pass results back through the DOM. When the pane is hidden its frames are throttled, so `?autoplay` misses notes there.
- Dev switches in the URL: `?autoplay` plays every note perfectly, `?node=N` starts the run at `RUN[N]` (7 = boss), `?coins=N` starts with coins. Runs with `autoplay` or `node` don't update the saved best.
- Keep timing logic driven by audio time. Never move gameplay forward based on input arrival.

## Other files

- `prototypes/town-and-layers.html`: the first top-down prototype, with town, combat, survival bars, ascent strain and rhythm ladders. Kept for reference. Its core-loop ideas (dive, push your luck, climb back with strain, rescue friends into the town) came before the chapter/level structure above and may or may not survive.
- `prototypes/style-lab.html`: early art-direction comparison (3D world plus pixel characters).

## Open questions

- The city, the landmarks, and the friends' looks and quirks.
- Boss gameplay: the Inspector is a placeholder. What should bosses really be?
- The upgrades: the prototype's set is a first guess. Which ones are fun, and what's the price curve?
- The vendor types and their currencies, beyond coins.
- Meta-progression: does anything carry over between runs (unlocks, new hats, friends rescued), or is every run a clean start?
- Whether the older ideas still apply: climbing back up (the ascent), and rescuing friends into the town (see `prototypes/town-and-layers.html`).
- Music: which songs go on which levels, and whether generated charts need hand touch-ups (an editor, or per-level overrides).
