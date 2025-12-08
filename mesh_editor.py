"""
メッシュエディター - 画像にポリゴンを描いて三角形メッシュを作成
すべての座標はスケール済み（ゲーム座標系）で保存
"""
import pygame
import json
import os
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, YELLOW, get_japanese_font


class TriangleMesh:
    """三角形メッシュの情報（すべてスケール済み座標）"""
    def __init__(self, center_x, center_y, color, triangles):
        self.center_x = center_x  # スケール済み重心X
        self.center_y = center_y  # スケール済み重心Y
        self.color = color
        self.triangles = triangles  # 重心からの相対座標（スケール済み）
    
    def to_dict(self):
        """辞書形式に変換"""
        return {
            "type": "triangulated_polygon",
            "center_x": self.center_x,
            "center_y": self.center_y,
            "color": self.color,
            "triangles": self.triangles
        }
    
    @classmethod
    def from_dict(cls, data):
        """辞書から作成"""
        return cls(
            data["center_x"],
            data["center_y"],
            data.get("color", (255, 0, 0)),
            data.get("triangles", [])
        )


class MeshEditor:
    """メッシュエディタークラス（三角形メッシュ専用）"""
    
    DEFAULT_SCALE = 0.15  # デフォルトスケール
    
    def __init__(self, scale=None):
        """エディターを初期化
        
        Args:
            scale: スケール値（0.0〜1.0）。Noneの場合はDEFAULT_SCALEを使用
        """
        pygame.init()
        
        # スケールを設定
        self.scale = scale if scale is not None else self.DEFAULT_SCALE
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"メッシュエディター (スケール: {self.scale})")
        self.clock = pygame.time.Clock()
        
        # 背景画像
        self.background_image = None  # スケール済み画像
        self.background_path = None
        self.image_offset_x = 0  # 画面上での画像オフセット
        self.image_offset_y = 0
        self.scaled_image_size = None  # スケール済み画像サイズ
        
        # 配置された三角形メッシュのリスト
        self.meshes = []
        
        # 選択中の色
        self.selected_color = RED
        
        # ポリゴン描画用
        self.drawing_polygon = False
        self.polygon_points = []  # スケール済み座標での点のリスト
    
    def load_background_image(self, image_path):
        """背景画像を読み込む（スケール済みで保持）"""
        try:
            original_image = pygame.image.load(image_path)
            self.background_path = image_path
            
            # 画像をスケール
            orig_w, orig_h = original_image.get_size()
            scaled_w = int(orig_w * self.scale)
            scaled_h = int(orig_h * self.scale)
            self.background_image = pygame.transform.scale(original_image, (scaled_w, scaled_h))
            self.scaled_image_size = (scaled_w, scaled_h)
            
            # 画面中央に配置
            self.image_offset_x = (SCREEN_WIDTH - scaled_w) // 2
            self.image_offset_y = (SCREEN_HEIGHT - scaled_h) // 2
            return True
        except Exception as e:
            print(f"画像の読み込みに失敗しました: {e}")
            return False
    
    def screen_to_game_coords(self, screen_x, screen_y):
        """画面座標をゲーム座標（スケール済み）に変換"""
        # 画像オフセットを引くだけ（すでにスケール済み座標系）
        game_x = screen_x - self.image_offset_x
        game_y = screen_y - self.image_offset_y
        return game_x, game_y
    
    def game_to_screen_coords(self, game_x, game_y):
        """ゲーム座標（スケール済み）を画面座標に変換"""
        screen_x = game_x + self.image_offset_x
        screen_y = game_y + self.image_offset_y
        return screen_x, screen_y
    
    def triangulate_polygon(self, vertices):
        """ポリゴンを三角分割（耳切り法）"""
        if len(vertices) < 3:
            return []
        
        v = list(vertices)
        triangles = []
        
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        # 面積を計算して向きを判定
        area = sum((v[i][0] * v[(i+1)%len(v)][1] - v[(i+1)%len(v)][0] * v[i][1]) 
                  for i in range(len(v))) / 2.0
        
        if area < 0:
            v.reverse()
        
        while len(v) > 3:
            ear_found = False
            for i in range(len(v)):
                prev_idx = (i - 1) % len(v)
                curr_idx = i
                next_idx = (i + 1) % len(v)
                
                prev = v[prev_idx]
                curr = v[curr_idx]
                next_v = v[next_idx]
                
                if cross_product(prev, curr, next_v) > 0:
                    is_ear = True
                    triangle = [prev, curr, next_v]
                    
                    for j in range(len(v)):
                        if j not in [prev_idx, curr_idx, next_idx]:
                            if self.point_in_triangle(v[j], triangle):
                                is_ear = False
                                break
                    
                    if is_ear:
                        triangles.append(triangle)
                        v.pop(curr_idx)
                        ear_found = True
                        break
            
            if not ear_found:
                if len(v) >= 3:
                    triangles.append([v[0], v[1], v[2]])
                    v.pop(1)
                else:
                    break
        
        if len(v) == 3:
            triangles.append(v)
        
        return triangles
    
    def point_in_triangle(self, point, triangle):
        """点が三角形の内部にあるかチェック"""
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        
        d1 = sign(point, triangle[0], triangle[1])
        d2 = sign(point, triangle[1], triangle[2])
        d3 = sign(point, triangle[2], triangle[0])
        
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        
        return not (has_neg and has_pos)
    
    def finish_polygon(self):
        """ポリゴンを完成して三角形メッシュに変換"""
        if len(self.polygon_points) < 3:
            return
        
        # 三角分割
        triangles = self.triangulate_polygon(self.polygon_points)
        
        if triangles:
            # 重心を計算（スケール済み座標）
            cx = sum(p[0] for p in self.polygon_points) / len(self.polygon_points)
            cy = sum(p[1] for p in self.polygon_points) / len(self.polygon_points)
            
            # 相対座標に変換（重心を原点に）
            relative_triangles = [
                [(v[0] - cx, v[1] - cy) for v in triangle]
                for triangle in triangles
            ]
            
            # メッシュを追加（すべてスケール済み座標）
            mesh = TriangleMesh(cx, cy, self.selected_color, relative_triangles)
            self.meshes.append(mesh)
            print(f"三角形メッシュを作成しました: {len(triangles)}個の三角形, 重心=({cx:.1f}, {cy:.1f})")
        
        self.drawing_polygon = False
        self.polygon_points = []
    
    def handle_events(self):
        """イベントを処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if not self.drawing_polygon:
                        self.drawing_polygon = True
                        self.polygon_points = []
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.drawing_polygon and len(self.polygon_points) >= 3:
                        self.finish_polygon()
                
                elif event.key == pygame.K_ESCAPE:
                    if self.drawing_polygon:
                        self.drawing_polygon = False
                        self.polygon_points = []
                
                elif event.key == pygame.K_c:
                    colors = [RED, (255, 100, 100), (100, 255, 100), (100, 100, 255), YELLOW]
                    current_idx = colors.index(self.selected_color) if self.selected_color in colors else 0
                    self.selected_color = colors[(current_idx + 1) % len(colors)]
                
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_mesh()
                elif event.key == pygame.K_o and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_mesh()
                
                elif event.key == pygame.K_r:
                    self.meshes.clear()
                    print("すべてのメッシュを削除しました")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    screen_x, screen_y = event.pos
                    
                    if self.drawing_polygon:
                        # スケール済み座標に変換して追加
                        game_x, game_y = self.screen_to_game_coords(screen_x, screen_y)
                        self.polygon_points.append((game_x, game_y))
                        
                        # 最初の点に近い位置をクリックしたら閉じる
                        if len(self.polygon_points) >= 3:
                            first = self.polygon_points[0]
                            dist = math.sqrt((game_x - first[0])**2 + (game_y - first[1])**2)
                            if dist < 15:
                                self.polygon_points.pop()  # 最後の点を削除（重複）
                                self.finish_polygon()
        
        return True
    
    def draw(self):
        """画面を描画"""
        self.screen.fill((50, 50, 50))
        
        # 背景画像を描画
        if self.background_image:
            self.screen.blit(self.background_image, (self.image_offset_x, self.image_offset_y))
        
        # ポリゴン描画中の線分を描画
        if self.drawing_polygon and len(self.polygon_points) > 0:
            for i, point in enumerate(self.polygon_points):
                screen_point = self.game_to_screen_coords(point[0], point[1])
                pygame.draw.circle(self.screen, self.selected_color, screen_point, 5)
                if i > 0:
                    prev_screen = self.game_to_screen_coords(
                        self.polygon_points[i-1][0], self.polygon_points[i-1][1]
                    )
                    pygame.draw.line(self.screen, self.selected_color, prev_screen, screen_point, 2)
            
            if len(self.polygon_points) >= 3:
                first_screen = self.game_to_screen_coords(
                    self.polygon_points[0][0], self.polygon_points[0][1]
                )
                last_screen = self.game_to_screen_coords(
                    self.polygon_points[-1][0], self.polygon_points[-1][1]
                )
                pygame.draw.line(self.screen, YELLOW, last_screen, first_screen, 2)
        
        # 配置された三角形メッシュを描画
        for mesh in self.meshes:
            for triangle in mesh.triangles:
                # 相対座標を絶対座標に変換
                abs_triangle = [
                    (mesh.center_x + v[0], mesh.center_y + v[1])
                    for v in triangle
                ]
                # 画面座標に変換
                screen_triangle = [
                    self.game_to_screen_coords(t[0], t[1])
                    for t in abs_triangle
                ]
                pygame.draw.polygon(self.screen, mesh.color, screen_triangle)
                pygame.draw.polygon(self.screen, BLACK, screen_triangle, 1)
        
        self.draw_ui()
        pygame.display.flip()
    
    def draw_ui(self):
        """UIを描画"""
        font = get_japanese_font(24)
        small_font = get_japanese_font(20)
        
        y_offset = 10
        
        text = "メッシュエディター（スケール済み座標）"
        text_surface = font.render(text, True, WHITE)
        self.screen.blit(text_surface, (10, y_offset))
        y_offset += 30
        
        if self.drawing_polygon:
            point_text = f"点の数: {len(self.polygon_points)} (Enter/Spaceで完成, Escでキャンセル)"
            text_surface = font.render(point_text, True, YELLOW)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30
        else:
            text = "W: 非凸ポリゴン描画開始"
            text_surface = font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30
        
        # 画像サイズ表示
        if self.scaled_image_size:
            size_text = f"画像サイズ: {self.scaled_image_size[0]}x{self.scaled_image_size[1]} (スケール済み)"
            text_surface = small_font.render(size_text, True, WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # 色のプレビュー
        y_offset += 10
        pygame.draw.circle(self.screen, self.selected_color, (25, y_offset), 15)
        pygame.draw.circle(self.screen, BLACK, (25, y_offset), 15, 2)
        text_surface = small_font.render("  色 (Cで切り替え)", True, WHITE)
        self.screen.blit(text_surface, (45, y_offset - 10))
        y_offset += 30
        
        # 操作説明
        instructions = [
            "W: ポリゴン描画",
            "クリック: 点を追加",
            "Enter/Space: 完成",
            "Esc: キャンセル",
            "R: 全削除",
            "Ctrl+S: 保存",
            "Ctrl+O: 読み込み",
        ]
        for instruction in instructions:
            text_surface = small_font.render(instruction, True, WHITE)
            self.screen.blit(text_surface, (SCREEN_WIDTH - 180, y_offset))
            y_offset += 22
        
        # 統計情報
        total_triangles = sum(len(mesh.triangles) for mesh in self.meshes)
        count_text = f"メッシュ数: {len(self.meshes)} | 三角形数: {total_triangles}"
        text_surface = font.render(count_text, True, WHITE)
        self.screen.blit(text_surface, (10, SCREEN_HEIGHT - 30))
    
    def save_mesh(self, filename="mesh.json"):
        """メッシュを保存（スケール済み座標）"""
        mesh_data = {
            "version": 2,  # 新形式
            "scale": self.scale,
            "background_image": self.background_path,
            "scaled_image_size": self.scaled_image_size,
            "shapes": [mesh.to_dict() for mesh in self.meshes]
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(mesh_data, f, indent=2, ensure_ascii=False)
            print(f"メッシュを保存しました: {filename}")
            return True
        except Exception as e:
            print(f"保存に失敗しました: {e}")
            return False
    
    def load_mesh(self, filename="mesh.json"):
        """メッシュを読み込み"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                mesh_data = json.load(f)
            
            # 背景画像を読み込み
            if "background_image" in mesh_data and mesh_data["background_image"]:
                image_path = mesh_data["background_image"]
                if not os.path.isabs(image_path):
                    mesh_dir = os.path.dirname(os.path.abspath(filename))
                    image_path = os.path.join(mesh_dir, os.path.basename(image_path))
                self.load_background_image(image_path)
            
            # メッシュを読み込み
            self.meshes = [
                TriangleMesh.from_dict(shape_data)
                for shape_data in mesh_data.get("shapes", [])
            ]
            
            print(f"メッシュを読み込みました: {filename}")
            return True
        except Exception as e:
            print(f"読み込みに失敗しました: {e}")
            return False
    
    def run(self):
        """エディターのメインループ"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
