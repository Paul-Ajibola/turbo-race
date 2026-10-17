"""Player car movement, input handling, and collision bounds."""

import pygame
from typing import Tuple
from src import constants


class Player:
    """Player car with movement, lives, invulnerability, and nitro state."""

    def __init__(self) -> None:
        self.width: int = constants.PLAYER_WIDTH
        self.height: int = constants.PLAYER_HEIGHT
        self.x: float = constants.SCREEN_WIDTH // 2 - self.width // 2
        self.y: float = constants.SCREEN_HEIGHT - self.height - 20
        self.speed_x: float = 0.0
        self.lives: int = constants.STARTING_LIVES
        self.invulnerable: int = 0
        self.nitro_active: int = 0
        self.nitro_cooldown: int = 0
        self.color: Tuple[int, int, int] = constants.NEON_CYAN

        self.rect: pygame.Rect = pygame.Rect(
            int(self.x), int(self.y), self.width, self.height
        )

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        road_left: int,
        road_right: int,
    ) -> None:
        """Update player position based on input and road boundaries."""
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.speed_x -= constants.PLAYER_ACCEL
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.speed_x += constants.PLAYER_ACCEL

        self.speed_x *= constants.PLAYER_FRICTION

        max_speed = constants.PLAYER_SPEED
        if self.nitro_active > 0:
            max_speed *= constants.NITRO_SPEED_BOOST
        if abs(self.speed_x) > max_speed:
            self.speed_x = max_speed if self.speed_x > 0 else -max_speed

        self.x += self.speed_x

        if self.x < road_left:
            self.x = float(road_left)
            self.speed_x = 0.0
        if self.x + self.width > road_right:
            self.x = float(road_right - self.width)
            self.speed_x = 0.0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.nitro_active > 0:
            self.nitro_active -= 1
        if self.nitro_cooldown > 0:
            self.nitro_cooldown -= 1

    def activate_nitro(self) -> None:
        """Activate nitro boost if not on cooldown and not already active.

        Arms both the boost duration and the recharge cooldown.
        """
        if self.nitro_cooldown == 0 and self.nitro_active == 0:
            self.nitro_active = constants.NITRO_DURATION_FRAMES
            self.nitro_cooldown = constants.NITRO_COOLDOWN_FRAMES

    def lose_life(self) -> bool:
        """Deduct one life and trigger invulnerability.

        Returns True if the player has no lives left (game over).
        """
        if self.invulnerable > 0:
            return False
        self.lives -= 1
        self.invulnerable = constants.INVULNERABILITY_FRAMES
        self.speed_x = 0.0
        return self.lives <= 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player car as a neon sprite."""
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0:
            return

        pygame.draw.rect(surface, self.color, self.rect)
        cockpit = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 15,
            self.width - 20,
            20,
        )
        pygame.draw.rect(surface, constants.BLACK, cockpit)
        wheel_w: int = 8
        wheel_h: int = 16
        pygame.draw.rect(
            surface, constants.BLACK,
            (self.rect.x - 4, self.rect.y + 10, wheel_w, wheel_h),
        )
        pygame.draw.rect(
            surface, constants.BLACK,
            (self.rect.x + self.width - 4, self.rect.y + 10, wheel_w, wheel_h),
        )
        pygame.draw.rect(
            surface, constants.BLACK,
            (self.rect.x - 4, self.rect.y + self.height - 26, wheel_w, wheel_h),
        )
        pygame.draw.rect(
            surface, constants.BLACK,
            (self.rect.x + self.width - 4, self.rect.y + self.height - 26, wheel_w, wheel_h),
        )
