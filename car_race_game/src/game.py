"""Main game loop, state management (Menu, Playing, Game Over)."""

import json
import pygame
from enum import Enum
from typing import Any
from src import constants
from src.entities.player import Player
from src.entities.obstacle import ObstacleManager
from src.systems.audio import AudioManager
from src.systems.physics import check_collision, check_near_miss
from src.systems.renderer import Renderer


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3


class Game:
    """Main game class handling state management and the deterministic game loop."""

    def __init__(self) -> None:
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Turbo Pixel Racer")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.renderer: Renderer = Renderer(self.screen)
        self.audio: AudioManager = AudioManager()
        self.audio.initialize()
        self.player: Player = Player()
        self.obstacle_manager: ObstacleManager = ObstacleManager()

        self.state: GameState = GameState.MENU
        self.score: int = 0
        self.bonus_score: int = 0
        self.high_score: int = self._load_high_score()
        self.scroll_speed: float = constants.OBSTACLE_BASE_SPEED
        self.distance: float = 0.0
        self.running: bool = True

    def _load_high_score(self) -> int:
        """Load the persisted high score (0 if missing or corrupt)."""
        try:
            if constants.HIGH_SCORE_FILE.exists():
                data: Any = json.loads(
                    constants.HIGH_SCORE_FILE.read_text(encoding="utf-8")
                )
                return max(0, int(data.get("high_score", 0)))
        except (OSError, ValueError, TypeError):
            pass
        return 0

    def _save_high_score(self) -> None:
        """Persist the high score; never crash on I/O errors."""
        try:
            constants.HIGH_SCORE_FILE.write_text(
                json.dumps({"high_score": self.high_score}),
                encoding="utf-8",
            )
        except OSError:
            pass

    def reset_game(self) -> None:
        """Reset all game state for a new run."""
        self.player = Player()
        self.obstacle_manager.reset()
        self.score = 0
        self.bonus_score = 0
        self.distance = 0.0
        self.scroll_speed = constants.OBSTACLE_BASE_SPEED
        self.state = GameState.PLAYING
        self.audio.start_engine()

    def handle_events(self) -> None:
        """Process Pygame input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.activate_nitro()

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False

    def update(self) -> None:
        """Update game logic for the current state."""
        if self.state != GameState.PLAYING:
            return

        keys: Any = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.scroll_speed = min(
                self.scroll_speed + constants.SCROLL_ACCEL,
                constants.PLAYER_MAX_SPEED,
            )
        else:
            self.scroll_speed *= constants.SCROLL_FRICTION

        if self.player.nitro_active > 0:
            self.scroll_speed = min(
                self.scroll_speed + constants.NITRO_SCROLL_ACCEL,
                constants.NITRO_MAX_SCROLL_SPEED,
            )

        if self.scroll_speed < constants.OBSTACLE_BASE_SPEED:
            self.scroll_speed = constants.OBSTACLE_BASE_SPEED

        self.player.update(
            keys, constants.ROAD_LEFT, constants.ROAD_RIGHT
        )

        self.obstacle_manager.spawn(self.scroll_speed)
        self.obstacle_manager.update(self.scroll_speed)

        self.distance += self.scroll_speed * constants.SCORE_PER_DISTANCE
        self.score = int(self.distance) + self.bonus_score

        if self.player.invulnerable == 0:
            for obstacle in self.obstacle_manager.obstacles:
                if check_collision(self.player.rect, obstacle.rect):
                    game_over: bool = self.player.lose_life()
                    self.audio.play_crash()
                    self.scroll_speed = constants.OBSTACLE_BASE_SPEED
                    if game_over:
                        self.state = GameState.GAME_OVER
                        self.audio.stop_engine()
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self._save_high_score()
                    break

        if self.player.invulnerable == 0:
            for obstacle in self.obstacle_manager.obstacles:
                if (
                    not obstacle.passed
                    and check_near_miss(self.player.rect, obstacle.rect)
                ):
                    self.bonus_score += constants.SCORE_NEAR_MISS
                    self.score = int(self.distance) + self.bonus_score
                    obstacle.passed = True
                    break

    def draw(self) -> None:
        """Render the current game state."""
        if self.state == GameState.MENU:
            self.renderer.draw_menu(self.high_score)

        elif self.state == GameState.PLAYING:
            self.renderer.draw_road(self.scroll_speed)
            self.renderer.draw_obstacles(self.obstacle_manager.obstacles)
            self.renderer.draw_player(self.player)
            self.renderer.draw_hud(
                self.score,
                self.player.lives,
                self.scroll_speed,
                self.player.nitro_active,
            )

        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_road(0.0)
            self.renderer.draw_obstacles(self.obstacle_manager.obstacles)
            self.renderer.draw_player(self.player)
            self.renderer.draw_game_over(self.score, self.high_score)

        pygame.display.flip()

    def run(self) -> None:
        """Run the deterministic 60 FPS game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(constants.FPS)

        self.audio.shutdown()
        pygame.quit()
