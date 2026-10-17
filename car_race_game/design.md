# Game design document (GDD) & feature roadmap
# Game Design Document (GDD): Turbo Pixel Racer

## 1. Overview
* **Genre:** 2D Top-Down Arcade Racer
* **Core Loop:** Drive a car along a continuously scrolling vertical road, dodge oncoming traffic/obstacles, survive as long as possible, and achieve a high score.
* **Target Platform:** Desktop (Python / Pygame)

---

## 2. Gameplay Mechanics
* **Controls:** 
  * `LEFT / RIGHT ARROW` (or `A / D`): Steer the car horizontally.
  * `UP ARROW` (or `W`): Accelerate / increase road scroll speed.
  * `SPACEBAR`: Nitro boost (limited duration).
* **Scoring System:** Score increases dynamically based on distance traveled and time survived. Bonus points awarded for near misses with obstacle cars.
* **Health / Lives:** The player starts with 3 lives. Colliding with an obstacle deducts 1 life, triggers a brief invulnerability flash, and resets speed.

---

## 3. Visual & Audio Style
* **Art Style:** 8-bit / 16-bit pixel art aesthetic with vibrant neon highlights.
* **Screen Resolution:** 800 x 600 pixels (fixed aspect ratio).
* **Audio:** Chiptune background music loop with synthesized engine humming and crash sound effects.

---

## 4. Game States
1. **Main Menu:** Title screen with "Press ENTER to Start" prompt and high-score display.
2. **Playing:** Active gameplay state with live HUD (Score, Lives, Speedometer).
3. **Game Over:** Summary screen displaying final score, high score, and prompt to restart or quit.

