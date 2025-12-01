"""
メッシュエディター - 画像にポリゴンを描いて三角分割メッシュを作成
"""
import pygame
import json
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, RED, YELLOW


class ShapePlacement:
    """三角分割されたポリゴンの情報"""
    def __init__(self, x, y, color, triangles):
        self.shape_type = "triangulated_polygon"
        self.x = x
        self.y = y
        self.color = color
        self.triangles = triangles
    
    def to_dict(self):
        """辞書形式に変換"""
        return {
            "type": self.shape_type,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "triangles": self.triangles
        }
    
    @classmethod
    def from_dict(cls, data):
        """辞書から作成"""
        return cls(
            data["x"],
            data["y"],
            data.get("color", (255, 0, 0)),
            data.get("triangles", [])
        )


class MeshEditor:
    """メッシュエディタークラス（ポリゴン分割のみ）"""
    
    def __init__(self):
        """エディターを初期化"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("メッシュエディター - ポリゴン分割")
        self.clock = pygame.time.Clock()
        
        # 背景画像
        self.background_image = None
        self.background_path = None
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.image_scale = 1.0
        
        # 配置されたポリゴンのリスト
        self.placed_shapes = []
        
        # 選択中の色
        self.selected_color = RED
        
        # ポリゴン描画用
        self.drawing_polygon = False
        self.polygon_points = []  # 画像座標系での点のリスト
        self.current_polygon_points = []  # 画面座標系での点のリスト（描画用）
    
    def load_background_image(self, image_path):
        """背景画像を読み込む"""
        try:
            self.background_image = pygame.image.load(image_path)
            self.background_path = image_path
            # 画像を画面サイズに合わせてスケール
            img_width, img_height = self.background_image.get_size()
            scale_x = SCREEN_WIDTH / img_width
            scale_y = SCREEN_HEIGHT / img_height
            self.image_scale = min(scale_x, scale_y, 1.0)  # 拡大しない
            scaled_width = int(img_width * self.image_scale)
            scaled_height = int(img_height * self.image_scale)
            self.background_image = pygame.transform.scale(
                self.background_image, (scaled_width, scaled_height)
            )
            # 中央に配置
            self.image_offset_x = (SCREEN_WIDTH - scaled_width) // 2
            self.image_offset_y = (SCREEN_HEIGHT - scaled_height) // 2
            return True
        except Exception as e:
            print(f"画像の読み込みに失敗しました: {e}")
            return False
    
    def screen_to_image_coords(self, screen_x, screen_y):
        """画面座標を画像座標に変換"""
        img_x = (screen_x - self.image_offset_x) / self.image_scale
        img_y = (screen_y - self.image_offset_y) / self.image_scale
        return img_x, img_y
    
    def image_to_screen_coords(self, img_x, img_y):
        """画像座標を画面座標に変換"""
        screen_x = img_x * self.image_scale + self.image_offset_x
        screen_y = img_y * self.image_scale + self.image_offset_y
        return screen_x, screen_y
    
    def triangulate_polygon(self, vertices):
        """
        ポリゴンを三角分割（耳切り法 - Ear Clipping Algorithm）
        
        Args:
            vertices: 頂点のリスト [(x1, y1), (x2, y2), ...]
        
        Returns:
            三角形のリスト [[(x1, y1), (x2, y2), (x3, y3)], ...]
        """
        if len(vertices) < 3:
            return []
        
        # 頂点のコピーを作成（変更可能にする）
        v = list(vertices)
        triangles = []
        
        # ポリゴンの向きを確認（時計回りか反時計回りか）
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        # 面積を計算して向きを判定
        area = sum((v[i][0] * v[(i+1)%len(v)][1] - v[(i+1)%len(v)][0] * v[i][1]) 
                  for i in range(len(v))) / 2.0
        
        # 反時計回りの場合は反転
        if area < 0:
            v.reverse()
        
        # 耳切り法で三角分割
        while len(v) > 3:
            ear_found = False
            for i in range(len(v)):
                # 3つの連続する頂点
                prev_idx = (i - 1) % len(v)
                curr_idx = i
                next_idx = (i + 1) % len(v)
                
                prev = v[prev_idx]
                curr = v[curr_idx]
                next_v = v[next_idx]
                
                # 三角形が凸かチェック
                if cross_product(prev, curr, next_v) > 0:
                    # 他の頂点が三角形の内部にないかチェック
                    is_ear = True
                    triangle = [prev, curr, next_v]
                    
                    for j in range(len(v)):
                        if j not in [prev_idx, curr_idx, next_idx]:
                            point = v[j]
                            if self.point_in_triangle(point, triangle):
                                is_ear = False
                                break
                    
                    if is_ear:
                        # 耳を見つけたので三角形として追加
                        triangles.append(triangle)
                        v.pop(curr_idx)
                        ear_found = True
                        break
            
            if not ear_found:
                # 耳が見つからない場合（自己交差など）、強制的に分割
                if len(v) >= 3:
                    triangles.append([v[0], v[1], v[2]])
                    v.pop(1)
                else:
                    break
        
        # 最後の三角形
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
        """ポリゴンを完成して三角分割"""
        if len(self.polygon_points) < 3:
            return
        
        # 三角分割
        triangles = self.triangulate_polygon(self.polygon_points)
        
        if triangles:
            # 重心を計算
            cx = sum(p[0] for p in self.polygon_points) / len(self.polygon_points)
            cy = sum(p[1] for p in self.polygon_points) / len(self.polygon_points)
            
            # 相対座標に変換（重心を原点に）
            relative_triangles = [
                [(v[0] - cx, v[1] - cy) for v in triangle]
                for triangle in triangles
            ]
            
            # 三角分割されたポリゴンを形状として追加
            shape = ShapePlacement(cx, cy, self.selected_color, relative_triangles)
            self.placed_shapes.append(shape)
            print(f"ポリゴンを三角分割しました: {len(triangles)}個の三角形")
        
        # 描画状態をリセット
        self.drawing_polygon = False
        self.polygon_points = []
        self.current_polygon_points = []
    
    def handle_events(self):
        """イベントを処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # ポリゴン描画開始/再開
                if event.key == pygame.K_w:
                    if not self.drawing_polygon:
                        self.drawing_polygon = True
                        self.polygon_points = []
                        self.current_polygon_points = []
                
                # ポリゴンを完成（三角分割）
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.drawing_polygon and len(self.polygon_points) >= 3:
                        self.finish_polygon()
                
                # ポリゴン描画をキャンセル
                elif event.key == pygame.K_ESCAPE:
                    if self.drawing_polygon:
                        self.drawing_polygon = False
                        self.polygon_points = []
                        self.current_polygon_points = []
                
                # 色の切り替え
                elif event.key == pygame.K_c:
                    colors = [RED, (255, 100, 100), (100, 255, 100), (100, 100, 255), YELLOW]
                    current_idx = colors.index(self.selected_color) if self.selected_color in colors else 0
                    self.selected_color = colors[(current_idx + 1) % len(colors)]
                
                # 保存/読み込み
                elif event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.save_mesh()
                elif event.key == pygame.K_o and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    self.load_mesh()
                
                # 全削除
                elif event.key == pygame.K_r:
                    self.placed_shapes.clear()
                    print("すべてのポリゴンを削除しました")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    x, y = event.pos
                    
                    if self.drawing_polygon:
                        # ポリゴンの点を追加
                        img_x, img_y = self.screen_to_image_coords(x, y)
                        self.polygon_points.append((img_x, img_y))
                        self.current_polygon_points.append((x, y))
                        
                        # 最初の点に近い位置をクリックしたら閉じる
                        if len(self.polygon_points) >= 3:
                            first_point = self.current_polygon_points[0]
                            dist = math.sqrt((x - first_point[0])**2 + (y - first_point[1])**2)
                            if dist < 20:  # 20ピクセル以内なら閉じる
                                self.finish_polygon()
        
        return True
    
    def draw(self):
        """画面を描画"""
        # 背景をクリア
        self.screen.fill((50, 50, 50))
        
        # 背景画像を描画
        if self.background_image:
            self.screen.blit(self.background_image, (self.image_offset_x, self.image_offset_y))
        
        # ポリゴン描画中の線分を描画
        if self.drawing_polygon and len(self.current_polygon_points) > 0:
            # 既存の点を描画
            for i, point in enumerate(self.current_polygon_points):
                pygame.draw.circle(self.screen, self.selected_color, point, 5)
                if i > 0:
                    # 線分を描画
                    pygame.draw.line(self.screen, self.selected_color, 
                                   self.current_polygon_points[i-1], point, 2)
            # 最初の点への線を描画（閉じる予定）
            if len(self.current_polygon_points) >= 3:
                pygame.draw.line(self.screen, YELLOW, 
                               self.current_polygon_points[-1], 
                               self.current_polygon_points[0], 2)
        
        # 配置されたポリゴンを描画
        for shape in self.placed_shapes:
            if shape.shape_type == "triangulated_polygon" and shape.triangles:
                for triangle in shape.triangles:
                    # 相対座標を絶対座標に変換
                    abs_triangle = [
                        (shape.x + v[0], shape.y + v[1])
                        for v in triangle
                    ]
                    # 画面座標に変換
                    screen_triangle = [
                        self.image_to_screen_coords(t[0], t[1]) 
                        for t in abs_triangle
                    ]
                    pygame.draw.polygon(self.screen, shape.color, screen_triangle)
                    pygame.draw.polygon(self.screen, BLACK, screen_triangle, 1)
        
        # UI情報を表示
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """UIを描画"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        y_offset = 10
        
        # タイトル
        text = "メッシュエディター - ポリゴン分割"
        text_surface = font.render(text, True, WHITE)
        self.screen.blit(text_surface, (10, y_offset))
        y_offset += 30
        
        # ポリゴン描画中の情報
        if self.drawing_polygon:
            point_text = f"点の数: {len(self.polygon_points)} (Enter/Spaceで完成, Escでキャンセル)"
            text_surface = font.render(point_text, True, YELLOW)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30
        else:
            text = "W: ポリゴン描画開始"
            text_surface = font.render(text, True, WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30
        
        # 色のプレビュー
        color_text = f"色: (Cで切り替え)"
        text_surface = font.render(color_text, True, WHITE)
        self.screen.blit(text_surface, (10, y_offset))
        y_offset += 30
        pygame.draw.circle(self.screen, self.selected_color, (150, y_offset - 15), 15)
        pygame.draw.circle(self.screen, BLACK, (150, y_offset - 15), 15, 2)
        y_offset += 30
        
        # 操作説明
        instructions = [
            "操作:",
            "W: ポリゴン描画開始",
            "クリック: 点を追加",
            "Enter/Space: 完成（三角分割）",
            "Esc: キャンセル",
            "C: 色切り替え",
            "R: 全削除",
            "Ctrl+S: 保存",
            "Ctrl+O: 読み込み",
        ]
        for instruction in instructions:
            text_surface = small_font.render(instruction, True, WHITE)
            self.screen.blit(text_surface, (SCREEN_WIDTH - 200, y_offset))
            y_offset += 25
        
        # 配置数
        count_text = f"ポリゴン数: {len(self.placed_shapes)}"
        text_surface = font.render(count_text, True, WHITE)
        self.screen.blit(text_surface, (10, SCREEN_HEIGHT - 30))
    
    def save_mesh(self, filename="mesh.json"):
        """メッシュを保存"""
        mesh_data = {
            "background_image": self.background_path,
            "shapes": [shape.to_dict() for shape in self.placed_shapes]
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
                self.load_background_image(mesh_data["background_image"])
            
            # 形状を読み込み
            self.placed_shapes = [
                ShapePlacement.from_dict(shape_data)
                for shape_data in mesh_data.get("shapes", [])
            ]
            
            print(f"メッシュを読み込みました: {filename}")
            return True
        except Exception as e:
            print(f"読み込みに失敗しました: {e}")
            return False
    
    def get_mesh_definition(self):
        """メッシュ定義を取得（NonConvexObject用）"""
        shape_definitions = []
        for shape in self.placed_shapes:
            if shape.shape_type == "triangulated_polygon" and shape.triangles:
                for triangle in shape.triangles:
                    # 相対座標を絶対座標に変換
                    abs_triangle = [
                        (shape.x + v[0], shape.y + v[1])
                        for v in triangle
                    ]
                    shape_definitions.append({
                        "type": "poly",
                        "vertices": abs_triangle
                    })
        return shape_definitions
    
    def run(self):
        """エディターのメインループ"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
