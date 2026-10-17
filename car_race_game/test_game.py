"""Smoke test for Turbo Pixel Racer: compile-checks all modules and runs
a headless simulation of Menu -> Playing -> Game Over without opening a window.
"""

import os
import sys
import py_compile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

MODULES = [
    "main.py",
    "src/constants.py",
    "src/game.py",
    "src/entities/player.py",
    "src/entities/obstacle.py",
    "src/systems/physics.py",
    "src/systems/renderer.py",
    "src/systems/audio.py",
]


def compile_all() -> None:
    for rel in MODULES:
        path = os.path.join(BASE, rel)
        py_compile.compile(path, doraise=True)
        print(f"OK compile: {rel}")


def smoke_test() -> None:
    import pygame
    from src.game import Game, GameState
    from src import constants
    from src.systems.physics import check_collision, check_near_miss, clamp_to_road

    # --- physics unit checks ---
    a = pygame.Rect(0, 0, 10, 10)
    b = pygame.Rect(5, 5, 10, 10)
    c = pygame.Rect(100, 100, 10, 10)
    assert check_collision(a, b), "overlapping rects must collide"
    assert not check_collision(a, c), "distant rects must not collide"
    assert clamp_to_road(0, 50, 200, 600) == 200, "clamp to left edge"
    assert clamp_to_road(580, 50, 200, 600) == 550, "clamp to right edge"
    near = pygame.Rect(20, 0, 10, 10)
    other = pygame.Rect(45, 15, 10, 10)
    assert check_near_miss(near, other), "adjacent rects are a near miss"
    print("OK physics checks")

    game = Game()
    assert game.state == GameState.MENU
    game.draw()

    # Start the game
    game.reset_game()
    assert game.state == GameState.PLAYING

    # Simulate 1200 frames of play (20 seconds @ 60 FPS)
    for _ in range(1200):
        game.handle_events()
        game.update()
        game.draw()
    print(f"OK 1200 frames simulated, score={game.score}, lives={game.player.lives}")

    # --- nitro: activation must arm duration AND cooldown ---
    p = game.player
    p.nitro_active = 0
    p.nitro_cooldown = 0
    p.activate_nitro()
    assert p.nitro_active == constants.NITRO_DURATION_FRAMES, "nitro duration"
    assert p.nitro_cooldown == constants.NITRO_COOLDOWN_FRAMES, "nitro cooldown armed"
    p.nitro_active = 0
    p.activate_nitro()
    assert p.nitro_active == 0, "nitro must not re-fire during cooldown"
    print("OK nitro cooldown armed")

    # --- collision: life lost, scroll speed reset, invulnerability ---
    from src.entities.obstacle import Obstacle

    game.reset_game()
    obs = Obstacle(lane=1, speed=constants.OBSTACLE_BASE_SPEED)
    obs.x = game.player.x
    obs.y = game.player.y
    obs.rect.x = int(obs.x)
    obs.rect.y = int(obs.y)
    game.obstacle_manager.obstacles = [obs]
    game.scroll_speed = 10.0
    game.update()
    assert game.player.lives == constants.STARTING_LIVES - 1, "collision loses a life"
    assert game.scroll_speed == constants.OBSTACLE_BASE_SPEED, "collision resets speed"
    assert game.player.invulnerable > 0, "invulnerability after hit"
    print("OK collision: life lost, speed reset, invulnerable")

    # --- audio: manager present; sounds synthesized or graceful no-op ---
    assert game.audio is not None
    if game.audio.enabled:
        game.audio.start_engine()
        game.audio.play_crash()
        game.audio.stop_engine()
        print("OK audio enabled: music, engine, crash synthesized")
    else:
        game.audio.play_crash()  # must be a safe no-op
        print("OK audio gracefully disabled (headless)")

    # --- near-miss bonus must persist across frames (no overwrite) ---
    game.reset_game()
    game.distance = 100.0
    obs2 = Obstacle(lane=0, speed=constants.OBSTACLE_BASE_SPEED)
    obs2.x = float(game.player.x + 60)
    obs2.y = float(game.player.rect.bottom - 35)
    obs2.rect.x = int(obs2.x)
    obs2.rect.y = int(obs2.y)
    game.obstacle_manager.obstacles = [obs2]
    game.update()
    assert game.bonus_score == constants.SCORE_NEAR_MISS, "near-miss awards bonus"
    game.update()
    assert game.score >= constants.SCORE_NEAR_MISS, "bonus persists across frames"
    print("OK near-miss bonus persists")

    # --- nitro must boost forward (scroll) speed beyond the UP cap ---
    game.reset_game()
    game.player.activate_nitro()
    for _ in range(60):
        game.update()
    assert game.scroll_speed > constants.PLAYER_MAX_SPEED, \
        "nitro exceeds normal max forward speed"
    print("OK nitro boosts forward speed")

    # --- ESC quits from gameplay ---
    import pygame as pg
    game.running = True
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))
    game.handle_events()
    assert game.running is False, "ESC must quit"
    game.running = True
    print("OK ESC quits")

    # --- bonus score resets on restart ---
    game.reset_game()
    assert game.bonus_score == 0, "bonus score resets on restart"
    print("OK bonus score resets")

    # Force game over
    game.player.lives = 1
    game.player.invulnerable = 0
    game.player.lose_life()
    game.state = GameState.GAME_OVER
    if game.score > game.high_score:
        game.high_score = game.score
    game.draw()
    assert game.state == GameState.GAME_OVER
    print(f"OK game over drawn, high_score={game.high_score}")

    # --- high score persisted to disk and reloadable ---
    import json
    game._save_high_score()
    assert constants.HIGH_SCORE_FILE.exists(), "high score file written"
    saved = json.loads(constants.HIGH_SCORE_FILE.read_text(encoding="utf-8"))
    assert saved["high_score"] == game.high_score, "persisted value matches"
    reloaded = Game._load_high_score(game)
    assert reloaded == game.high_score, "high score reload matches"
    print("OK high score persisted and reloaded")

    # Restart flow
    game.reset_game()
    assert game.state == GameState.PLAYING
    assert game.player.lives == constants.STARTING_LIVES
    assert len(game.obstacle_manager.obstacles) == 0
    print("OK restart flow")

    pygame.quit()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    compile_all()
    smoke_test()
