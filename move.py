import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 最初の画面更新（←これがあると切り替えが確実に見える）
screen.fill((255, 255, 255))
pygame.display.update()

# キャラ位置と設定
x = WIDTH // 2
y = HEIGHT // 2
speed = 5
angle = 0
size = 40

def rotate_point(px, py, cx, cy, ang):
    rad = math.radians(ang)
    dx = px - cx
    dy = py - cy
    nx = dx * math.cos(rad) - dy * math.sin(rad)
    ny = dx * math.sin(rad) + dy * math.cos(rad)
    return (int(cx + nx), int(cy + ny))

# runningで制御できるように変更（これ使っても使わなくてもOK）
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # ループ終了制御

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        x -= speed
    if keys[pygame.K_RIGHT]:
        x += speed
    if keys[pygame.K_a]:
        angle += 4
    if keys[pygame.K_d]:
        angle -= 4

    # 三角形（上・左下・右下）
    p1 = (x, y - size)
    p2 = (x - size, y + size)
    p3 = (x + size, y + size)

    rp1 = rotate_point(*p1, x, y, angle)
    rp2 = rotate_point(*p2, x, y, angle)
    rp3 = rotate_point(*p3, x, y, angle)

    screen.fill((255, 255, 255))  # 白背景
    pygame.draw.polygon(screen, (0, 0, 0), [rp1, rp2, rp3])  # 黒三角

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
