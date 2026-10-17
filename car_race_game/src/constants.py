"""Screen dimensions, colors, frame rates, and game speeds."""

from pathlib import Path
from typing import Tuple, List

# ---------------------------------------------------------------------------
# Screen settings
# ---------------------------------------------------------------------------
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

# ---------------------------------------------------------------------------
# Colors (RGB)
# ---------------------------------------------------------------------------
WHITE: Tuple[int, int, int] = (255, 255, 255)
BLACK: Tuple[int, int, int] = (0, 0, 0)
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)
GRAY: Tuple[int, int, int] = (128, 128, 128)
DARK_GRAY: Tuple[int, int, int] = (64, 64, 64)
ROAD_GRAY: Tuple[int, int, int] = (80, 80, 80)
GRASS_GREEN: Tuple[int, int, int] = (34, 139, 34)
YELLOW: Tuple[int, int, int] = (255, 255, 0)
NEON_PINK: Tuple[int, int, int] = (255, 0, 255)
NEON_CYAN: Tuple[int, int, int] = (0, 255, 255)

# ---------------------------------------------------------------------------
# Road settings
# ---------------------------------------------------------------------------
ROAD_WIDTH: int = 400
ROAD_LEFT: int = (SCREEN_WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT: int = ROAD_LEFT + ROAD_WIDTH
LANE_COUNT: int = 3
LANE_WIDTH: int = ROAD_WIDTH // LANE_COUNT

# ---------------------------------------------------------------------------
# Player settings
# ---------------------------------------------------------------------------
PLAYER_WIDTH: int = 50
PLAYER_HEIGHT: int = 80
PLAYER_SPEED: float = 6.0
PLAYER_MAX_SPEED: float = 14.0
SCROLL_ACCEL: float = 0.15
SCROLL_FRICTION: float = 0.985
PLAYER_ACCEL: float = 0.45
PLAYER_FRICTION: float = 0.96
STARTING_LIVES: int = 3
INVULNERABILITY_FRAMES: int = 120

# ---------------------------------------------------------------------------
# Obstacle settings
# ---------------------------------------------------------------------------
OBSTACLE_WIDTH: int = 50
OBSTACLE_HEIGHT: int = 80
OBSTACLE_BASE_SPEED: float = 4.0
OBSTACLE_SPEED_INCREMENT: float = 0.12
OBSTACLE_SPAWN_FRAMES: int = 90
OBSTACLE_MIN_SPAWN_FRAMES: int = 45

# ---------------------------------------------------------------------------
# Nitro settings
# ---------------------------------------------------------------------------
NITRO_DURATION_FRAMES: int = 180
NITRO_SPEED_BOOST: float = 2.5
NITRO_COOLDOWN_FRAMES: int = 300
NITRO_SCROLL_ACCEL: float = 0.35
NITRO_MAX_SCROLL_SPEED: float = 20.0

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
SCORE_PER_DISTANCE: float = 0.1
SCORE_NEAR_MISS: int = 50
NEAR_MISS_DISTANCE: int = 40

# ---------------------------------------------------------------------------
# Asset paths (pathlib for cross-platform compatibility)
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
ASSETS_DIR: Path = BASE_DIR / "assets"
IMAGES_DIR: Path = ASSETS_DIR / "images"
SOUNDS_DIR: Path = ASSETS_DIR / "sounds"
HIGH_SCORE_FILE: Path = BASE_DIR / "high_score.json"
