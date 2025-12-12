import pygame
import subprocess

pygame.init()

screen = pygame.display.set_mode((1200, 800))
screen_width, screen_height = screen.get_size()
screen.fill((105, 205, 245))
pygame.display.set_caption("Test")
image = pygame.image.load("meshes/mesh1/texsture.png")
image_width, image_height = image.get_size()
small_image = pygame.transform.scale(image, (image_width//5, image_height//5))
center_x = screen_width//2
center_y = screen_height//2
button_radius = 80
rect_size = screen_width//2
triangle_size = 60
triangle_edge = 2/1.732 * triangle_size


Running = True
while Running:
    #足場
    pygame.draw.rect(screen, (71, 154, 84), pygame.Rect(center_x - rect_size//2, 750, rect_size, 50), 0)
    #画像
    screen.blit(small_image, (300, 350))
    #タイトル
    font = pygame.font.Font("C:/Windows/Fonts/HGRPP1.TTC", 80)
    text = font.render('にんげんタワーバトル', True, (110, 110, 110))
    text_rect = text.get_rect(center=(center_x+3, 150+3))
    screen.blit(text, text_rect)
    text = font.render('にんげんタワーバトル', True, (255, 255, 255))
    text_rect = text.get_rect(center=(center_x, 150))
    screen.blit(text, text_rect)
    #スタートボタン
    pygame.draw.circle(screen, (245, 197, 67), (center_x+5, center_y+5), button_radius, 10)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), button_radius, 10)
    points = ((center_x + triangle_size*2//3, center_y), (center_x - triangle_size//3, center_y + triangle_edge/2), (center_x - triangle_size//3, center_y - triangle_edge/2))
    points_under = [(x + 5, y + 5) for (x, y) in points]
    pygame.draw.polygon(screen, (245, 197, 67), points_under, 0)
    pygame.draw.polygon(screen, (255, 255, 255), points, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  
            Running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos   # マウス座標
            bx, by = center_x, center_y

            # 中心との距離を計算して円内を判定
            if (mx - bx)**2 + (my - by)**2 <= button_radius**2:
                subprocess.Popen(["python", "test_game.py"])  # ←test_game.py起動
                Running = False  # START画面を終了（これがあると「完全に切り替え」になる）

    
    pygame.display.update()