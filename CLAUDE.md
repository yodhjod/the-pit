# The Pit

A mobile web game made for a group of friends. The player descends a giant pit that opened in the middle of their city, in the spirit of Made in Abyss. The friends appear in the game as characters, but none of them is the main player.

## Direction from the group

- Must run on both Android and iPhone in the browser, with no install. Touch first, keyboard as a fallback.
- Genres voted: adventure/RPG (Pokémon Black/White, X/Y era), hack 'n' slash, survival.
- Tone: sarcastic and parodic on the surface, genuinely dark underneath. The rim town is a tourist trap and the bureaucracy is absurd (delver permits, "NO REFUNDS" signs).
- The real city and its landmarks will anchor the setting. Not decided yet: which city, which places, the friends' names and looks.

## Current focus: `index.html` (Pit Descent)

A rhythm-game vertical slice of the descent, in side view.

- **The world keeps the beat.** The explorer walks down one stair per beat automatically. Their position is a pure function of song time (see the hero section in `frame()`), so the visuals stay on the beat even when the player misses. Input only changes the outcome: a quiet tiptoe or a creak and stumble, a vault or a bonk, a duck or a bat hit, riding the zipline or dangling.
- **One stair = one beat.** Half-beat notes get half-width stairs. Zipline spans have no stairs underneath.
- **Actions:** tap = tiptoe, swipe up = vault, swipe down = duck, hold = zipline (let go on the landing beat).
- **Layers:** Rim, Drowned Metro, Ossuary, Spore Gardens, Depths. Each has its own palette, decor, obstacle, creature, music mode and BPM (88, 96, 100, 108, 84).
- **Stakes:** 5 lanterns (hearts). One is refilled per new layer. Losing them all restarts the current layer.
- **Feedback:** the rhythm track at the bottom is the main timing UI, with an early/late meter. There's also a ring under the finger, a fixed marker on the stair of the next action, and a flash when its beat hits.
- **Explorer:** a rigged pixel-art sprite generated in code (`drawPose` and `POSES`). Its walk is a comedic sneaky tiptoe: the knee lifts before the beat, then a long toe-first stride lands on the beat. Poses are skeleton coordinates, so friends can be built later by swapping hat, hair, glasses and colours.

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
- The chart lives in `CHART`: per layer, `[beat, type, holdBeats]`, with type `t`/`u`/`d`/`h`. `STAIR` is derived from it.

## Reading `index.html` cheaply

The file is ~90 KB of dense one-line code, so don't read it whole. Grep `/\* ----------` to list the sections with line numbers, then read only the range you need. Sections, in order: utils · chart · world constants · lighting · pit wall · instancing · rim · path platforms · signs · obstacles/ziplines/swoopers · layers 0–4 decor · glow points · light shafts · particles · creatures · explorer (`drawPose`, `POSES`) · sparkles · audio (`clock`, `musicBeat`) · action cues · game state (judging, `setupRun`, `start`, `finish`) · input + calibration · gauge · next-action marker + beat flashes · rhythm track (`drawTrack`) · frame loop (`frame`).

## Conventions

- Keep the game a single HTML file unless it grows past the point of being workable. Prefer small, surgical edits.
- Test in a headless Chromium (Playwright with `--use-gl=swiftshader`). Software rendering is slow, so judge visuals from screenshots, not timing accuracy.
- Keep timing logic driven by audio time. Never move gameplay forward based on input arrival.

## Other files

- `prototypes/town-and-layers.html`: the first top-down prototype, with town, combat, survival bars, ascent strain and rhythm ladders. Kept for reference. The core-loop ideas from it (dive, push your luck, climb back with strain, rescue friends into the town) are still the plan for the full game.
- `prototypes/style-lab.html`: early art-direction comparison (3D world plus pixel characters).

## Open questions

- The city, the landmarks, and the friends' looks and quirks.
- How the rhythm descent fits into the full game. For example: the descent is the travel between layers, and exploration and combat happen on each layer.
- Climbing back up (the ascent): does it reuse the rhythm system in reverse, and is it harder?
- Music: a composed track whose melody matches the chart would make the rhythm much easier to read.
