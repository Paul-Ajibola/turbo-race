"""Generate cover.png (1600x1000, 16:10) for start.ng using pygame, offscreen."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.font.init()

W, H = 1600, 1000
surf = pygame.Surface((W, H))
surf.fill((34, 139, 34))  # grass

ROAD_W = 800
ROAD_LEFT = (W - ROAD_W) // 2
pygame.draw.rect(surf, (80, 80, 80), (ROAD_LEFT, 0, ROAD_W, H))
pygame.draw.line(surf, (255, 255, 0), (ROAD_LEFT, 0), (ROAD_LEFT, H), 8)
pygame.draw.line(surf, (255, 255, 0), (ROAD_LEFT + ROAD_W, 0), (ROAD_LEFT + ROAD_W, H), 8)

LANE_W = ROAD_W // 3
for lane in (1, 2):
    x = ROAD_LEFT + lane * LANE_W
    y = -40
    while y < H:
        pygame.draw.line(surf, (255, 255, 255), (x, y), (x, y + 80), 6)
        y += 120


def car(x, y, color, scale=2.8):
    """Same sprite recipe as the game: body, cockpit, four wheels."""
    w, h = int(50 * scale), int(80 * scale)
    pygame.draw.rect(surf, color, (x, y, w, h))
    pygame.draw.rect(surf, (0, 0, 0), (x + int(10 * scale), y + int(15 * scale),
                                       w - int(20 * scale), int(20 * scale)))
    ww, wh = int(8 * scale), int(16 * scale)
    for wx, wy in ((x - int(4 * scale), y + int(10 * scale)),
                   (x + w - 4, y + int(10 * scale)),
                   (x - int(4 * scale), y + h - int(26 * scale)),
                   (x + w - 4, y + h - int(26 * scale))):
        pygame.draw.rect(surf, (0, 0, 0), (wx, wy, ww, wh))


car(ROAD_LEFT + 25, 640, (0, 255, 255))            # player, neon cyan
car(ROAD_LEFT + LANE_W + 25, 330, (255, 0, 255))   # rival, neon pink
car(ROAD_LEFT + 2 * LANE_W + 25, 140, (255, 0, 0))  # rival, red

# Dark band for the title
band = pygame.Surface((W, 320))
band.set_alpha(205)
band.fill((10, 10, 14))
surf.blit(band, (0, 0))

big = pygame.font.Font(None, 150)
mid = pygame.font.Font(None, 76)
small = pygame.font.Font(None, 54)

title = big.render("TURBO PIXEL RACER", True, (0, 255, 255))
surf.blit(title, title.get_rect(center=(W // 2, 110)))

subtitle = mid.render("Dodge traffic. Survive. Score high.", True, (255, 255, 255))
surf.blit(subtitle, subtitle.get_rect(center=(W // 2, 215)))

tag = small.render("A start.ng browser racer", True, (255, 255, 0))
surf.blit(tag, tag.get_rect(center=(W // 2, 285)))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cover.png")
pygame.image.save(surf, out)
print("saved", out, os.path.getsize(out), "bytes")

