"""
ゲームの設定ファイル
"""
import pygame

# 画面サイズ
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 物理エンジンの設定
GRAVITY = (0, 981)  # 重力（下向き）
FPS = 60

# 動物の設定
ANIMAL_SIZE = 50
ANIMAL_MASS = 10

# 地面の設定
GROUND_HEIGHT = 50
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT


