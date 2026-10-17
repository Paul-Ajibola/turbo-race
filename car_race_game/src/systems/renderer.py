"""Drawing background scrolling, sprites, and HUD UI."""

import pygame
from typing import List, Tuple
from src import constants
from src.entities.player import Player
from src.entities.obstacle import Obstacle


class Renderer:
    """Handles all drawing operations for the game."""

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface: pygame.Surface = surface
        self.font_large: pygame.font.Font = pygame.font.Font(None, 72)
        self.font_medium: pygame.font.Font = pygame.font.Font(None, 48)
        self.font_small: pygame.font.Font = pygame.font.Font(None, 32)
        self.road_offset: float = 0.0

    def _advance_road_offset(self, scroll_speed: float) -> None:
        self.road_offset = (self.road_offset + scroll_speed) % 40

    def draw_road(self, scroll_speed: float) -> None:
        """Draw the scrolling road, grass shoulders, and lane markings."""
        self._advance_road_offset(scroll_speed)

        self.surface.fill(constants.GRASS_GREEN)

        road_rect: pygame.Rect = pygame.Rect(
            constants.ROAD_LEFT, 0,
            constants.ROAD_WIDTH, constants.SCREEN_HEIGHT,
        )
        pygame.draw.rect(self.surface, constants.ROAD_GRAY, road_rect)

        pygame.draw.line(
            self.surface, constants.YELLOW,
            (constants.ROAD_LEFT, 0),
            (constants.ROAD_LEFT, constants.SCREEN_HEIGHT),
            4,
        )
        pygame.draw.line(
            self.surface, constants.YELLOW,
            (constants.ROAD_RIGHT, 0),
            (constants.ROAD_RIGHT, constants.SCREEN_HEIGHT),
            4,
        )

        dash_height: int = 40
        dash_gap: int = 20
        for lane in range(1, constants.LANE_COUNT):
            lane_x: int = constants.ROAD_LEFT + lane * constants.LANE_WIDTH
            y: float = self.road_offset
            while y < constants.SCREEN_HEIGHT:
                pygame.draw.line(
                    self.surface, constants.WHITE,
                    (lane_x, int(y)),
                    (lane_x, int(y + dash_height)),
                    3,
                )
                y += dash_height + dash_gap

    def draw_player(self, player: Player) -> None:
        player.draw(self.surface)

    def draw_obstacles(self, obstacles: List[Obstacle]) -> None:
        for obstacle in obstacles:
            obstacle.draw(self.surface)

    def draw_hud(
        self,
        score: int,
        lives: int,
        speed: float,
        nitro_frames: int,
    ) -> None:
        """Draw the heads-up display (score, lives, speed, nitro)."""
        score_text: pygame.Surface = self.font_small.render(
            f"Score: {score}", True, constants.WHITE
        )
        self.surface.blit(score_text, (20, 20))

        lives_text: pygame.Surface = self.font_small.render(
            f"Lives: {lives}", True, constants.WHITE
        )
        self.surface.blit(lives_text, (20, 50))

        speed_text: pygame.Surface = self.font_small.render(
            f"Speed: {speed:.1f}", True, constants.WHITE
        )
        self.surface.blit(speed_text, (20, 80))

        nitro_color: Tuple[int, int, int] = (
            constants.NEON_CYAN if nitro_frames > 0 else constants.GRAY
        )
        nitro_label: str = "ACTIVE" if nitro_frames > 0 else "READY"
        nitro_text: pygame.Surface = self.font_small.render(
            f"Nitro: {nitro_label}", True, nitro_color
        )
        self.surface.blit(nitro_text, (20, 110))

    def draw_menu(self, high_score: int) -> None:
        """Draw the main menu screen."""
        self.surface.fill(constants.BLACK)

        title: pygame.Surface = self.font_large.render(
            "TURBO PIXEL RACER", True, constants.NEON_CYAN
        )
        title_rect: pygame.Rect = title.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 200)
        )
        self.surface.blit(title, title_rect)

        subtitle: pygame.Surface = self.font_medium.render(
            "Dodge traffic. Survive. Score high.", True, constants.WHITE
        )
        subtitle_rect: pygame.Rect = subtitle.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 270)
        )
        self.surface.blit(subtitle, subtitle_rect)

        hs_text: pygame.Surface = self.font_small.render(
            f"High Score: {high_score}", True, constants.YELLOW
        )
        hs_rect: pygame.Rect = hs_text.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 330)
        )
        self.surface.blit(hs_text, hs_rect)

        controls: List[str] = [
            "LEFT / RIGHT or A / D : Steer",
            "UP or W                 : Accelerate",
            "SPACE                     : Nitro Boost",
        ]
        for i, line in enumerate(controls):
            ctrl: pygame.Surface = self.font_small.render(line, True, constants.WHITE)
            ctrl_rect: pygame.Rect = ctrl.get_rect(
                center=(constants.SCREEN_WIDTH // 2, 400 + i * 30)
            )
            self.surface.blit(ctrl, ctrl_rect)

        start: pygame.Surface = self.font_medium.render(
            "Press ENTER to Start", True, constants.GREEN
        )
        start_rect: pygame.Rect = start.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 510)
        )
        self.surface.blit(start, start_rect)

    def draw_game_over(self, score: int, high_score: int) -> None:
        """Draw the game-over screen."""
        overlay: pygame.Surface = pygame.Surface(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        )
        overlay.set_alpha(185)
        overlay.fill(constants.BLACK)
        self.surface.blit(overlay, (0, 0))

        go_text: pygame.Surface = self.font_large.render(
            "GAME OVER", True, constants.RED
        )
        go_rect: pygame.Rect = go_text.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 220)
        )
        self.surface.blit(go_text, go_rect)

        score_text: pygame.Surface = self.font_medium.render(
            f"Final Score: {score}", True, constants.WHITE
        )
        score_rect: pygame.Rect = score_text.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 300)
        )
        self.surface.blit(score_text, score_rect)

        hs_text: pygame.Surface = self.font_small.render(
            f"High Score: {high_score}", True, constants.YELLOW
        )
        hs_rect: pygame.Rect = hs_text.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 350)
        )
        self.surface.blit(hs_text, hs_rect)

        restart: pygame.Surface = self.font_medium.render(
            "Press ENTER to Restart", True, constants.GREEN
        )
        restart_rect: pygame.Rect = restart.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 430)
        )
        self.surface.blit(restart, restart_rect)

        quit_text: pygame.Surface = self.font_medium.render(
            "Press Q to Quit", True, constants.RED
        )
        quit_rect: pygame.Rect = quit_text.get_rect(
            center=(constants.SCREEN_WIDTH // 2, 480)
        )
        self.surface.blit(quit_text, quit_rect)
