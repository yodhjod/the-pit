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

- **The run** (`RUN`): Rim → Drowned Metro → vendor → Ossuary → Spore Gardens → vendor → Depths → boss. Each descent level is one 16-beat layer with a count-in, then a "Level cleared" screen with its fixed lore line. Lanterns and coins carry over between levels; losing all lanterns ends the run. The deepest node reached is saved in localStorage (`pitBest`) and shown on the title and death screens.
- **Coins:** Perfect = 2, Good = 1, plus upgrade bonuses.
- **Vendors** (`openVendor`, `UPG`): each vendor node lists how many items to roll per tier; stock is random per run, items already owned are skipped. Upgrades are flags in `G.up` checked where they apply (`score`, `loseHeart`, `fail`, `relight`), or change the timing windows `W_P`/`W_G`/`W_S` directly.
- **Boss** (`startBoss`, `BOSSN`, `BOSSG`): the Inspector, a giant eye in a cap. The explorer stands still at the bottom camp. Same four actions: tap = strike, hold = charged strike, swipe up/down = dodge its low sweep / high swipe. Before a sweep the iris takes the cue colour and the eye winds up, then lunges on the beat. 40 HP, the 32-beat chart loops 3 times; if it runs out, the run ends. Placeholder for the boss design.

- **The world keeps the beat.** The explorer walks down one stair per beat automatically. Their position is a pure function of song time (see the hero section in `frame()`), so the visuals stay on the beat even when the player misses. Input only changes the outcome: a quiet tiptoe or a creak and stumble, a vault or a bonk, a duck or a bat hit, riding the zipline or dangling.
- **One stair = one beat.** Half-beat notes get half-width stairs. Zipline spans have no stairs underneath.
- **Actions:** tap = tiptoe, swipe up = vault, swipe down = duck, hold = zipline (let go on the landing beat).
- **Layers:** Rim, Drowned Metro, Ossuary, Spore Gardens, Depths. Each has its own palette, decor, obstacle, creature, music mode and BPM (88, 96, 100, 108, 84). The boss runs at 112 on beats 80+.
- **Stakes:** 5 lanterns (hearts). One is relit per new level.
- **Feedback:** the rhythm track at the bottom is the main timing UI, with an early/late meter. There's also a ring under the finger, a fixed marker on the stair of the next action, and a flash when its beat hits.
- **Explorer:** a rigged pixel-art sprite generated in code (`drawPose` and `POSES`). Its walk is a cartoon sneak (modelled on a classic sneak-cycle reference): hunched forward and low on tiptoe, arms swinging low and opposite to the legs like a march, hands dangling, swapping with each step (`armSwap`); the far leg and arm are drawn much darker so the alternation reads at small size. The knee lifts high before the beat, then a long toe-first stride lands on the beat. Poses are skeleton coordinates, so friends can be built later by swapping hat, hair, glasses and colours.

## Tech

- Single self-contained HTML file. No build step.
- Three.js r128 from cdnjs (UMD global `THREE`). Google Fonts: Cormorant Garamond and IBM Plex Mono.
- All art is procedural: low-poly toon-shaded geometry, instanced decor, canvas textures, pixel sprites drawn into canvases.
- All audio is procedural Web Audio: a pad, bass, arpeggio and kick per layer, generated per beat in `musicBeat`.
- **Timing:**
  - `timeOf(beat)` maps chart beats to AudioContext time. Tempo changes per layer are handled by `songT`.
  - `clock()` returns the *heard* time: it compensates output latency and is smoothed against `performance.now()`.
  - Inputs use the event's own `timeStamp` through `clockAt()`.
  - The audio delay offset (`offsetMs`) is user-set or measured with the Calibrate screen, and saved in localStorage.
- The chart lives in `CHART`: per layer, `[beat, type, holdBeats]`, with type `t`/`u`/`d`/`h`. `STAIR` is derived from it. The boss chart is `BOSS_CHART`, same format. `ACT` is the note list being judged (`NOTES` or `BOSSN`); `G.endB` is the current level's last beat.

## Reading `index.html` cheaply

The file is ~100 KB of dense one-line code, so don't read it whole. Grep `/\* ----------` to list the sections with line numbers, then read only the range you need. Sections, in order: utils · chart · the run (`RUN`, `UPG`, boss chart) · world constants · lighting · pit wall · instancing · rim · path platforms · signs · obstacles/ziplines/swoopers · layers 0–4 decor · glow points · light shafts · particles · creatures · explorer (`drawPose`, `POSES`) · chapter boss (3D model) · sparkles · audio (`clock`, `musicBeat`) · action cues · game state (judging, `score`, `loseHeart`) · run flow (`newRun`, `startLevel`, `levelClear`, `openVendor`, `startBoss`, `fallOut`, `finish`) · input + calibration · gauge · next-action marker + beat flashes · rhythm track (`drawTrack`) · frame loop (`frame`).

## Conventions

- Keep the game a single HTML file unless it grows past the point of being workable. Prefer small, surgical edits.
- Test in a headless Chromium (Playwright with `--use-gl=swiftshader`), or in the desktop app's browser pane via the `the-pit` server in `.claude/launch.json` (serves the folder on http://localhost:8123). Software rendering is slow, so judge visuals from screenshots, not timing accuracy.
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
- Music: a composed track whose melody matches the chart would make the rhythm much easier to read.
