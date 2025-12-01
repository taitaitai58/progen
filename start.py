import pygame
import subprocess

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("START画面")

running = True
while running:
    screen.fill((0,0,75))

    font = pygame.font.SysFont(None,80)
    message = font.render("START(sキーをクリック)", False, (255,255,255))
    screen.blit(message, (200,300))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                subprocess.Popen(["python", "move.py"])  # ←move.py起動
                running = False  # START画面を終了（これがあると「完全に切り替え」になる）

    pygame.display.update()

pygame.quit()
