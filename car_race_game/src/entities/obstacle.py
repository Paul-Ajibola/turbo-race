"""Enemy traffic cars and roadside barriers."""

import random
import pygame
from typing import List, Tuple
from src import constants


class Obstacle:
    """A single enemy traffic car."""

    COLORS: List[Tuple[int, int, int]] = [
        constants.RED,
        constants.BLUE,
        constants.YELLOW,
        constants.NEON_PINK,
        constants.GREEN,
    ]

    def __init__(self, lane: int, speed: float) -> None:
        self.width: int = constants.OBSTACLE_WIDTH
        self.height: int = constants.OBSTACLE_HEIGHT
        self.lane: int = lane
        self.speed: float = speed
        self.passed: bool = False

        lane_x: int = constants.ROAD_LEFT + lane * constants.LANE_WIDTH
        self.x: float = lane_x + (constants.LANE_WIDTH - self.width) // 2
        self.y: float = -self.height

        self.color: Tuple[int, int, int] = random.choice(self.COLORS)

        self.rect: pygame.Rect = pygame.Rect(
            int(self.x), int(self.y), self.width, self.height
        )

    def update(self, scroll_speed: float) -> None:
        """Move the obstacle down the screen."""
        self.y += self.speed + scroll_speed * 0.5
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def is_off_screen(self) -> bool:
        """Return True if the obstacle has moved past the bottom edge."""
        return self.y > constants.SCREEN_HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the obstacle car."""
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


class ObstacleManager:
    """Spawns, updates, and draws all obstacles."""

    def __init__(self) -> None:
        self.obstacles: List[Obstacle] = []
        self.spawn_timer: int = 0

    def spawn(self, scroll_speed: float) -> None:
        """Attempt to spawn a new obstacle based on current speed."""
        self.spawn_timer += 1
        spawn_rate: int = max(
            constants.OBSTACLE_MIN_SPAWN_FRAMES,
            constants.OBSTACLE_SPAWN_FRAMES - int(scroll_speed * 6),
        )

        if self.spawn_timer >= spawn_rate:
            lane: int = random.randint(0, constants.LANE_COUNT - 1)
            self.obstacles.append(Obstacle(lane, constants.OBSTACLE_BASE_SPEED))
            self.spawn_timer = 0

    def update(self, scroll_speed: float) -> None:
        """Update all obstacles and remove those off-screen."""
        for obstacle in self.obstacles:
            obstacle.update(scroll_speed)
        self.obstacles = [
            obs for obs in self.obstacles if not obs.is_off_screen()
        ]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw every active obstacle."""
        for obstacle in self.obstacles:
            obstacle.draw(surface)

    def reset(self) -> None:
        """Clear all obstacles and reset the spawn timer."""
        self.obstacles.clear()
        self.spawn_timer = 0
