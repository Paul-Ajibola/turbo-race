"""Collision detection and movement boundaries."""

import pygame
from src import constants


def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """Return True if two axis-aligned bounding boxes overlap."""
    return rect1.colliderect(rect2)


def check_near_miss(player_rect: pygame.Rect, obstacle_rect: pygame.Rect) -> bool:
    """Return True if the player nearly passed the obstacle without hitting it."""
    horizontal_close: bool = (
        player_rect.right > obstacle_rect.left - constants.NEAR_MISS_DISTANCE
        and player_rect.left < obstacle_rect.right + constants.NEAR_MISS_DISTANCE
    )
    vertical_close: bool = abs(player_rect.bottom - obstacle_rect.top) < constants.NEAR_MISS_DISTANCE
    return horizontal_close and vertical_close


def clamp_to_road(x: float, width: int, road_left: int, road_right: int) -> float:
    """Clamp an x-coordinate so the object stays inside the road."""
    if x < road_left:
        return float(road_left)
    if x + width > road_right:
        return float(road_right - width)
    return x
