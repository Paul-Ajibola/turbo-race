# AI coding agent instructions & guidelines
# AI Agent Instructions: Retro Car Racer

## Project Context
You are assisting in the development of a 2D top-down retro car racing game built using Python and Pygame. The focus is on clean architecture, smooth 60 FPS performance, and strict separation of concerns between game logic, rendering, and input handling.

## Core Engineering Guidelines
1. **Separation of Concerns:** Keep entity logic (`src/entities/`) independent of rendering logic (`src/systems/renderer.py`). Entities should update their own positions and states; systems should handle drawing and collision physics.
2. **Modular Constants:** Never hardcode magic numbers (colors, speeds, screen dimensions). Always reference `src/constants.py`.
3. **Clean Code & Typing:** Write PEP 8 compliant Python code. Use type hints for all function signatures and class attributes.
4. **Error Handling & Robustness:** Ensure asset loading paths use `pathlib` for cross-platform compatibility and handle missing asset fallbacks gracefully.

## Coding Workflow
- When implementing a feature, update the corresponding module in `src/`.
- Maintain a deterministic game loop inside `src/game.py` using Pygame's `clock.tick(60)` to lock frame rates.