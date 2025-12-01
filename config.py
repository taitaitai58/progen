"""
ゲームの設定ファイル
"""
import pygame
import sys
import platform

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


def get_japanese_font(size):
    """
    日本語対応フォントを取得
    
    Args:
        size: フォントサイズ
    
    Returns:
        pygame.font.Font: 日本語対応フォント
    """
    # システムに応じた日本語フォントを取得
    system = platform.system()
    
    # 利用可能な日本語フォントのリスト
    japanese_fonts = []
    
    if system == "Darwin":  # macOS
        japanese_fonts = [
            "Hiragino Maru Gothic ProN",
            "Hiragino Sans",
            "Hiragino Kaku Gothic ProN",
            "AppleGothic",
            "Osaka",
        ]
    elif system == "Windows":
        japanese_fonts = [
            "MS Gothic",
            "MS PGothic",
            "Yu Gothic",
            "Meiryo",
        ]
    elif system == "Linux":
        japanese_fonts = [
            "Noto Sans CJK JP",
            "Noto Sans JP",
            "IPAexGothic",
            "IPAPGothic",
            "VL Gothic",
        ]
    
    # 利用可能なフォントを試す
    for font_name in japanese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            # テスト用に日本語文字をレンダリングしてみる
            test_surface = font.render("テスト", True, (0, 0, 0))
            if test_surface.get_width() > 0:
                return font
        except:
            continue
    
    # フォールバック: システムのデフォルトフォントを使用
    try:
        return pygame.font.SysFont(None, size)
    except:
        # 最終的なフォールバック
        return pygame.font.Font(None, size)


