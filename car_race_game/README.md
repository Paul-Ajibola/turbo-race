# 🏎️ Turbo Pixel Racer

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame 2.1+](https://img.shields.io/badge/Pygame-2.1%2B-FF6B35?logo=pygame&logoColor=white)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 20+ checks](https://img.shields.io/badge/Tests-20%2B%20checks-passing-brightgreen)](#testing)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-success)](#)

> **A neon-soaked 2D top-down arcade racer built with Python and Pygame.**
> Dodge endless procedurally-spawned traffic on a scrolling 3-lane highway,
> thread daring near-misses for bonus points, burn nitro to surge past the
> speed limit, and chase a high score that persists between sessions.

**Zero asset files needed** — cars, road, HUD, music, engine hum, and crash
sound effects are all generated procedurally at runtime. Clone, install one
dependency, and race.

```bash
pip install -r requirements.txt
python main.py
```

## Table of Contents

- [Overview](#overview)
- [Highlights](#highlights)
- [Screenshots](#screenshots)
- [Gameplay](#gameplay)
- [Controls](#controls)
- [Installation](#installation)
- [Running the Game](#running-the-game)
- [Testing](#testing)
- [Architecture](#architecture)
- [Module Reference](#module-reference)
- [Configuration and Tuning](#configuration-and-tuning)
- [Audio Design](#audio-design)
- [Visual Design](#visual-design)
- [High-Score Persistence](#high-score-persistence)
- [Design-Document Compliance](#design-document-compliance)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Credits](#credits)

## Overview

Turbo Pixel Racer is a complete, self-contained arcade game following the
classic "endless racer" formula: an overhead view of a three-lane road scrolls
toward you while you steer between oncoming cars. Every second you survive
earns points, traffic thickens as you push the car harder, and one mistake
costs a life. The run ends at zero lives — then the chase for the high score
begins again.

The codebase is deliberately clean and idiomatic:

- **Entities vs. systems separation** — game objects (`player.py`,
  `obstacle.py`) hold state; gameplay logic lives in systems
  (`physics.py`, `renderer.py`, `audio.py`)
- **Every magic number lives in [`src/constants.py`](src/constants.py)** —
  one file to tune the entire game
- **Fully type-hinted, PEP 8**, `pathlib` for all file paths
- **Deterministic 60 FPS loop** with a state machine
  (`MENU → PLAYING → GAME_OVER → MENU`)

## Highlights

- ✅ **Endless procedural gameplay** — traffic spawn rate scales with speed
- ✅ **3 lives** with a 2-second blinking invulnerability window after each hit
- ✅ **Nitro boost** — 3-second forward surge that breaks the normal speed cap,
  with a fair 5-second recharge
- ✅ **Near-miss rewards** — skim past a car within 40 px for **+50 points**
- ✅ **Persistent high score** — saved to `high_score.json`, shown on the menu
  after restarts and reboots
- ✅ **Procedural audio** — looping square-wave chiptune soundtrack, speed-
  reactive engine hum, decaying-noise crash SFX; graceful no-op if no audio
  device is present
- ✅ **Procedural neon art** — no image assets required; everything is drawn
  with primitives (optional PNG support is the planned upgrade path)
- ✅ **Fully tested** — headless test suite covering physics, a 20-second
  simulated run, collision rules, nitro cooldowns, scoring persistence, and
  more

## Screenshots

*(Run the game and press <kbd>PrtScn</kbd> to add real screenshots — until
then, here's what you're in for.)*

**Menu screen**

```
┌──────────────────────────────────────────────────┐
│                                                  │
│              T U R B O   P I X E L               │
│                  R A C E R                       │
│          Dodge traffic. Survive. Score high.     │
│                 High Score: 12480                │
│    LEFT/RIGHT or A/D : Steer                     │
│      UP or W         : Accelerate                │
│       SPACE          : Nitro Boost               │
│            Press ENTER to Start                  │
└──────────────────────────────────────────────────┘
```

**In-race HUD** — score, lives, speed, and nitro status stay out of the way
in the top-left corner while the road scrolls beneath you:

```
┌──────────────────────────────────────────────────┐
│ Score: 4871                                       │
│ Lives: ♥ ♥ _                                      │
│ Speed: 11.4                                       │
│ Nitro: ████████░░ READY (SPACE)                   │
│        ┌───────────────────────┐                  │
│        │  ◆ (blue traffic)    │                  │
│        │         ▲ you        │                  │
│        │   ◆             ◆   │                  │
│        │       ◆    ◆        │                  │
│        └───────────────────────┘                  │
└──────────────────────────────────────────────────┘
```

**Game over** — a dark overlay freezes the action and presents your final
score, the high score, and a one-key restart:

```
┌──────────────────────────────────────────────────┐
│                 ══ GAME OVER ══                  │
│                  Final Score: 6210               │
│                  High Score:  12480              │
│          Press ENTER to Restart                  │
│              Press Q to Quit                     │
└──────────────────────────────────────────────────┘
```

## Gameplay

### Core Loop

1. **Menu** — read the controls, see the high score, press <kbd>Enter</kbd>
2. **Race** — survive as long as possible while traffic thickens
3. **Game over** — the third hit ends the run; review your score, then
   restart with one keypress (player, spawner, and score fully reset)
4. **Repeat** — beat the high score, which persists to disk forever

### Speed Model

The world scrolls downward past your car at `scroll_speed` (pixels/frame),
starting at **4.0**:

- Holding <kbd>↑</kbd>/<kbd>W</kbd> accelerates at **+0.15/frame** up to the
  normal cap of **14.0**
- **Nitro** accelerates at **+0.35/frame** and raises the cap to **20.0** —
  you visibly surge forward
- Releasing the gas decays speed **×0.985/frame** back toward the base 4.0
- A crash slams you back to base speed instantly
- Lateral steering ramps at 0.45 px/frame² up to a max of **6.0 px/frame**
  (×2.5 while nitro is active)

### Scoring

```
score = ⌊ Σ (scroll_speed × 0.1) ⌋  +  50 × (number of near-misses)
```

Distance points tick up every frame, so going faster earns faster — speed is
literally risk. Near-miss bonuses are accumulated separately and are never
lost to rounding or resets. Your final score is compared against the
persisted high score when the run ends.

### Lives and Damage

- You start each run with **3 lives** (❤❤❤ in the HUD)
- Colliding with a traffic car: **−1 life**, scroll speed reset to base,
  crash sound effect
- After a hit you are **invulnerable for 2 seconds** (120 frames) and blink
  visibly — this prevents chain-drain from a single mistake
- At **0 lives**: Game Over, overlay appears, high score saved if beaten

### Nitro Boost

Press <kbd>Space</kbd> when the meter reads `READY`:

| Phase | Duration | Effect |
| --- | --- | --- |
| **Active** | 3 s (180 frames) | Forward accel past the cap (up to 20.0) and steering ×2.5 |
| **Recharge** | 5 s (300 frames) | Meter refills; cannot fire early |
| **Ready** | — | HUD shows `Nitro: ██████ READY (SPACE)` |

The cooldown arms cleanly on activation and only starts counting down after
the burst ends, so a fresh game always allows an immediate first nitro.

### Near-Miss Bonuses

As each traffic car passes your car, if the two cars are within **40 px on
both axes** (a genuine squeeze), you bank **+50 points** with an on-screen
`+50` pop-up and a confirmation blip. Each car awards this **at most once** —
you can't farm the same car by wiggling back and forth.

### Difficulty Progression

Traffic density is a function of your speed, not the clock:

```
spawn_interval = max(45, 90 − 6 × scroll_speed) frames
```

At idle speed a car appears roughly every 1.5 seconds; at full speed roughly
every 0.75 seconds — twice the traffic, closing at nearly twice the rate.
Because speed also multiplies your score rate, the game constantly asks:
*do you slow down and play safe, or push through the chaos for points?*

## Controls

| Key | Action |
| --- | --- |
| <kbd>←</kbd> <kbd>→</kbd> or <kbd>A</kbd> <kbd>D</kbd> | Steer left / right |
| <kbd>↑</kbd> or <kbd>W</kbd> | Accelerate (raises scroll speed) |
| <kbd>Space</kbd> | Fire nitro boost (when charged) |
| <kbd>Enter</kbd> | Start race (menu) · Restart race (game over) |
| <kbd>Esc</kbd> | Quit from any state |
| <kbd>Q</kbd> | Quit (game over screen) |

*Click the game window first if keystrokes aren't registering — the window
must have OS focus.*

## Installation

### Prerequisites

- **Python 3.9+** (developed and tested on 3.11) — [python.org](https://www.python.org/downloads/)
- **Pygame 2.1+** (tested on 2.6.1) — the only third-party dependency
- A sound card/audio device is optional; the game runs (and stays silent)
  without one

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/Paul-Ajibola/turbo-pixel-racer.git
cd turbo-pixel-racer

# 2. (Recommended) create an isolated environment
python -m venv .venv
#   Windows:
.venv\Scripts\activate
#   macOS / Linux:
source .venv/bin/activate

# 3. Install the dependency
pip install -r requirements.txt

# 4. Confirm the install
python -c "import pygame; print(pygame.version.ver)"
```

## Running the Game

```bash
python main.py
```

A window titled **Turbo Pixel Racer** opens at **800×600**. You'll land on
the menu with chiptune music playing — press <kbd>Enter</kbd> and dodge.

## Testing

A fully headless test suite (no window, no audio device — uses SDL dummy
drivers) validates the whole game:

```bash
python test_game.py
```

It covers:

- Compilation of every module
- Road-scrolling and collision physics math
- A **1,200-frame simulated run** (~20 seconds of real gameplay) with live
  assertions on lives, speed bounds, and state integrity
- Nitro cooldown arming (no early re-fire, instant first use)
- Collision consequences (life loss, speed reset, invulnerability window)
- Procedural audio synthesis (music, engine hum, crash all generated)
- Near-miss bonus **persistence** (the bonus is never wiped by scoring)
- Nitro **forward-speed effect** (it must actually beat the normal cap)
- <kbd>Esc</kbd> quit handling
- Game-over overlay and high-score save/reload across sessions
- Restart flow (clean state reset)

Expected output ends with:

```
ALL TESTS PASSED
```

## Architecture

```
car_race_game/
├── main.py                  # Entry point: pygame init → Game().run()
├── requirements.txt         # pygame>=2.1.0
├── test_game.py             # Headless validation suite
├── high_score.json          # Created at runtime (git-ignored)
├── LICENSE
├── README.md
├── assets/
│   ├── images/.gitkeep      # Optional PNG sprites (procedural fallback)
│   └── sounds/.gitkeep      # Optional audio files (procedural fallback)
└── src/
    ├── __init__.py
    ├── constants.py         # EVERY tunable value, commented
    ├── game.py              # Game class: loop, state machine, input, score
    ├── entities/
    │   ├── __init__.py
    │   ├── player.py        # Player car entity
    │   └── obstacle.py      # Traffic car entity + ObstacleManager spawner
    └── systems/
        ├── __init__.py
        ├── physics.py       # Collision + near-miss detection
        ├── renderer.py      # Road, sprites, HUD, menus (all drawing)
        └── audio.py         # AudioManager: procedural SFX + music
```

Design principles (from the project's engineering guidelines):

1. **Entities hold state, systems hold behavior** — `Player` knows its
   position and lives; `physics.py` decides what happens when cars meet
2. **One source of truth for tuning** — no number appears inline in logic;
   everything is imported from `constants.py`
3. **Fail-safe presentation and audio** — the renderer and audio manager are
   pure side-effects of game state; if audio init fails, the game continues
   silently instead of crashing
4. **Deterministic simulation** — all timing is frame-based at a fixed 60 FPS
   cap, so the test suite can simulate thousands of frames headlessly

### Frame-by-frame data flow

```
pygame events ──► Game.handle_events()   (input, state transitions)
                       │
                       ▼
              Game.update()              (only in PLAYING state)
               ├─ scroll_speed physics (accel / nitro / decay)
               ├─ Player.update()        (steering, nitro timers)
               ├─ ObstacleManager.update() (spawn + movement)
               ├─ physics.check_collisions() (hits, near-misses)
               └─ distance → score, high-score check on death
                       │
                       ▼
              Game.render()              (always: menu/playing/game over)
               ├─ draw_road(), draw_obstacles(), draw_player()
               ├─ HUD: score, lives, speed, nitro meter
               └─ menu / game-over overlays
                       │
                       ▼
              clock.tick(60)             (frame pacing)
```

## Module Reference

| Module | Key contents |
| --- | --- |
| [`main.py`](main.py) | Bootstraps pygame, creates the display/audio, runs `Game().run()` |
| [`src/constants.py`](src/constants.py) | Screen (800×600, 60 FPS), road geometry (400 px, 3 lanes), player (speeds, lives, invulnerability), obstacles (spawn curve), nitro (durations, boosts), scoring (rates, near-miss) |
| [`src/game.py`](src/game.py) | `Game` class — `run()` loop, `handle_events()` (incl. <kbd>Esc</kbd> quit), `update()` (speed physics, scoring), `render()` state dispatch, `reset_game()`, high-score load/save |
| [`src/entities/player.py`](src/entities/player.py) | `Player` — `update()` (clamped steering, nitro timers), `trigger_crash()`, `draw()` (procedural neon car with headlight glow), `reset()` |
| [`src/entities/obstacle.py`](src/entities/obstacle.py) | `Obstacle` (colored traffic car) and `ObstacleManager` — speed-scaled spawning, off-screen cleanup, lane-based placement |
| [`src/systems/physics.py`](src/systems/physics.py) | `check_collisions()` — AABB overlap → damage + invulnerability; `check_near_miss()` — passed-car squeeze detection (once per car) |
| [`src/systems/renderer.py`](src/systems/renderer.py) | `draw_road()` (scrolling stripes, animated lane markers, neon edges), `draw_car()` helper, `draw_player()`, `draw_hud()` (score/lives/speed/nitro meter), menu + game-over screens |
| [`src/systems/audio.py`](src/systems/audio.py) | `AudioManager` — synthesizes a 2.4 s A-minor square-wave chiptune loop, a 55/110 Hz sine engine hum keyed to speed, and a 0.45 s decaying-noise crash; every method is a safe no-op if the mixer is unavailable |

## Configuration and Tuning

Every gameplay value lives in [`src/constants.py`](src/constants.py) — change
a number, restart, and the whole game feels different. Current values:

### Screen & Road

| Constant | Value | Effect |
| --- | --- | --- |
| `SCREEN_WIDTH × SCREEN_HEIGHT` | 800 × 600 | Window size (px) |
| `FPS` | 60 | Frame cap; all timings are frame-based |
| `ROAD_WIDTH` | 400 | Playable road; grass fills the rest |
| `LANE_COUNT` | 3 | Traffic lanes (`LANE_WIDTH` = 133 px) |

### Player

| Constant | Value | Effect |
| --- | --- | --- |
| `PLAYER_WIDTH × PLAYER_HEIGHT` | 50 × 80 | Car hitbox/draw size |
| `PLAYER_SPEED` | 6.0 | Max lateral steering speed (px/frame) |
| `PLAYER_ACCEL` | 0.45 | Lateral acceleration per frame |
| `PLAYER_FRICTION` | 0.96 | Lateral speed decay per frame |
| `PLAYER_MAX_SPEED` | 14.0 | Top scroll speed with <kbd>↑</kbd> held |
| `SCROLL_ACCEL` | 0.15 | Forward accel per frame while accelerating |
| `SCROLL_FRICTION` | 0.985 | Speed decay per frame when coasting |
| `STARTING_LIVES` | 3 | Lives per run |
| `INVULNERABILITY_FRAMES` | 120 | Post-crash mercy window (2 s, blinking) |

### Traffic

| Constant | Value | Effect |
| --- | --- | --- |
| `OBSTACLE_WIDTH × OBSTACLE_HEIGHT` | 50 × 80 | Traffic car size (same as player) |
| `OBSTACLE_BASE_SPEED` | 4.0 | Base scroll speed = idle world speed |
| `OBSTACLE_SPAWN_FRAMES` | 90 | Spawn interval at idle speed |
| `OBSTACLE_MIN_SPAWN_FRAMES` | 45 | Fastest spawn interval |
| `OBSTACLE_SPEED_INCREMENT` | 0.12 | *Reserved* — future difficulty ramp (see [Roadmap](#roadmap)) |

### Nitro

| Constant | Value | Effect |
| --- | --- | --- |
| `NITRO_DURATION_FRAMES` | 180 | Burst length (3 s) |
| `NITRO_COOLDOWN_FRAMES` | 300 | Recharge time (5 s) |
| `NITRO_SCROLL_ACCEL` | 0.35 | Forward accel during burst |
| `NITRO_MAX_SCROLL_SPEED` | 20.0 | Hard speed ceiling during burst |
| `NITRO_SPEED_BOOST` | 2.5 | Lateral speed multiplier during burst |

### Scoring

| Constant | Value | Effect |
| --- | --- | --- |
| `SCORE_PER_DISTANCE` | 0.1 | Points per frame per unit of speed |
| `SCORE_NEAR_MISS` | 50 | Bonus per qualifying squeeze |
| `NEAR_MISS_DISTANCE` | 40 | Max px separation (both axes) to qualify |

## Audio Design

All sound is synthesized at startup with the Python `array` module — no
`.ogg`/`.wav` files ship with the game:

- **Music** — a 16-note, 2.4-second **A-minor arpeggio** in square wave
  (150 ms per note), mixed at volume 0.35 and looped forever
- **Engine hum** — a seamless 1-second loop combining 55 Hz and 110 Hz sine
  waves at volume 0.5, playing only while you're racing; it starts and stops
  with your run
- **Crash** — 0.45 seconds of white noise shaped by an exponential decay
  envelope at volume 0.8

The mixer opens at 44,100 Hz, 16-bit, stereo. If **no audio device exists**
(headless CI, muted VM, broken drivers), the `AudioManager` flips a single
`self.enabled` flag and every play call becomes a silent no-op — the game
never crashes over sound.

## Visual Design

- **Road** — dark asphalt with scrolling dashed lane markers, alternating
  shoulder stripes in neon pink/cyan, and a subtle speed line effect; the
  stripe offset is driven by `scroll_speed`, so the road visually reacts to
  acceleration and nitro
- **Cars** — procedurally drawn rectangles with colored body, dark windows,
  and neon outlines; your car is cyan, traffic cycles through blue/green/
  yellow/red/purple
- **HUD** — semi-transparent dark panel, top-left: `Score`, `Lives` (hearts),
  `Speed` (1 decimal), and a `Nitro` meter showing `READY (SPACE)`, a
  draining bar, or the recharge countdown
- **Feedback** — the player blinks every 4 frames while invulnerable; `+50`
  pop-ups appear at near-miss locations; the game-over screen dims the frozen
  scene

## High-Score Persistence

When a run ends, if your score beats the stored record, the game writes:

```json
{ "high_score": 12480 }
```

…to `high_score.json` next to `main.py` (path built with `pathlib`, so it
works on every OS). On startup the file is read back; a missing or corrupted
file simply resets the record to 0 — never an error. The file is
git-ignored, so clones start fresh.

## Design-Document Compliance

The game was built to the accompanying game design document (`design.md`).
Feature-to-GDD mapping:

| GDD Requirement | Status | Where |
| --- | --- | --- |
| 2D top-down endless racer, 800×600 @ 60 FPS | ✅ | `constants.py`, `game.py` |
| 3-lane scrolling road with animated markings | ✅ | `renderer.draw_road()` |
| Player car: steer, accelerate, speed cap | ✅ | `player.py`, `game.update()` |
| 3 lives + post-crash invulnerability | ✅ | `player.py` |
| Procedurally spawned traffic obstacles | ✅ | `obstacle.ObstacleManager` |
| Collision detection with penalties | ✅ | `physics.check_collisions()` |
| Scoring: distance + bonuses | ✅ | `game.update()`, `physics.check_near_miss()` |
| Nitro boost mechanic | ✅ | `player.py`, `constants.py` (NITRO_*) |
| Menu / Playing / Game Over states | ✅ | `GameState` machine in `game.py` |
| High-score persistence | ✅ | `game._save_high_score()` |
| Audio: music + engine + crash SFX | ✅ | `audio.AudioManager` (procedural) |
| Roadside barriers / obstacle variety | 🔶 | Traffic cars implemented; barrier variety on the [Roadmap](#roadmap) |

## Roadmap

Ideas for the next iteration — none are required for a complete game:

- 🎨 **Pixel-art sprites** — drop PNGs into `assets/images/` and extend the
  renderer's loader to use them with procedural fallback
- 🎵 **Richer soundtrack** — real `.ogg` tracks through the same
  `AudioManager` API, plus per-lane passing whooshes
- 🚧 **Obstacle variety** — static barriers and oil slicks using the
  reserved `OBSTACLE_SPEED_INCREMENT` difficulty ramp
- ⏸️ **Pause state** — a `PAUSED` game state (<kbd>P</kbd>) with a resume
  overlay
- 🎮 **Gamepad support** — SDL joystick steering and triggers
- ✨ **Juice** — tire particles, speed lines at max velocity, screen shake on
  impact, combo multiplier for chained near-misses

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'pygame'` | Activate your virtual environment and run `pip install -r requirements.txt` |
| Window opens then closes instantly | Run `python main.py` from a terminal and read the traceback — most often a wrong working directory |
| Keys do nothing | Click the game window first; it needs OS focus |
| No sound | Expected without an audio device — the game stays fully playable. Check OS volume/mute otherwise |
| Game feels too hard/easy | Tune `STARTING_LIVES`, `OBSTACLE_SPAWN_FRAMES`, or `PLAYER_MAX_SPEED` in `src/constants.py` |
| Want a fresh high score | Delete `high_score.json` |
| `python` not found on Windows/py | Use `py main.py` instead |

## License

Released under the [MIT License](LICENSE) — free to use, modify, and
distribute.

## Credits

- **Design, code, and procedural art/audio** — [Paul-Ajibola](https://github.com/Paul-Ajibola)
- Built with [Pygame](https://www.pygame.org/) and the Python standard library
- Thanks to the arcade greats — *OutRun*, *Spy Hunter*, and every roadside
  cabinet that taught us to dodge traffic

---

<p align="center">
  <b>Start your engines — <code>python main.py</code> 🏁</b>
</p>





