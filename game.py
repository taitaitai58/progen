"""
ゲームのメインロジック
"""
import pygame
import pymunk
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY, FPS,
    GROUND_HEIGHT, GROUND_Y, BLACK, GREEN
)
from animals import Animal, ANIMALS, NonConvexObject, NON_CONVEX_SHAPES, ANIMAL_MASS
import json


class Game:
    """ゲームのメインクラス"""
    
    def __init__(self):
        """ゲームを初期化"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("動物タワーバトル")
        self.clock = pygame.time.Clock()
        
        # 物理空間の作成
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        
        # 動物のリスト
        self.animals = []
        
        # 非凸物体のリスト
        self.non_convex_objects = []
        
        # 地面の作成
        self.create_ground()
        
        # 選択中の動物タイプ
        self.selected_animal_type = "cat"
        self.animal_types = list(ANIMALS.keys())
        
        # 選択中の非凸物体タイプ
        self.selected_shape_type = "L"
        self.shape_types = list(NON_CONVEX_SHAPES.keys())
        
        # モード切り替え（動物モード or 非凸物体モード）
        self.mode = "animal"  # "animal" or "non_convex"
        
        # カスタムメッシュ（エディターで作成したメッシュ）
        self.custom_meshes = {}  # メッシュ名 -> メッシュ定義
        self.custom_mesh_images = {}  # メッシュ名 -> 画像パス
        self.custom_mesh_scale = 0.2  # メッシュのスケール（1/5）
        self.custom_mesh_image_pos = (10, 100)  # 画像の表示位置
        
    def create_ground(self):
        """地面を作成"""
        # 地面のボディ（静的）
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        ground_shape = pymunk.Segment(
            ground_body,
            (0, GROUND_Y),
            (SCREEN_WIDTH, GROUND_Y),
            5
        )
        ground_shape.friction = 1.0
        self.space.add(ground_body, ground_shape)
        
        # 左側の壁
        left_wall = pymunk.Body(body_type=pymunk.Body.STATIC)
        left_wall_shape = pymunk.Segment(
            left_wall,
            (0, 0),
            (0, SCREEN_HEIGHT),
            5
        )
        left_wall_shape.friction = 1.0
        self.space.add(left_wall, left_wall_shape)
        
        # 右側の壁
        right_wall = pymunk.Body(body_type=pymunk.Body.STATIC)
        right_wall_shape = pymunk.Segment(
            right_wall,
            (SCREEN_WIDTH, 0),
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            5
        )
        right_wall_shape.friction = 1.0
        self.space.add(right_wall, right_wall_shape)
    
    def handle_events(self):
        """イベントを処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # マウスクリックで動物または非凸物体を追加
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    x, y = event.pos
                    if self.mode == "animal":
                        # クリック位置に動物を追加
                        animal_info = ANIMALS[self.selected_animal_type]
                        animal = Animal(
                            self.space,
                            x, y,
                            animal_info["color"],
                            self.selected_animal_type,
                            animal_info["mass"]
                        )
                        self.animals.append(animal)
                    else:  # non_convex mode
                        # クリック位置に非凸物体を追加
                        if self.selected_shape_type in NON_CONVEX_SHAPES:
                            # プリセット形状
                            shape_info = NON_CONVEX_SHAPES[self.selected_shape_type]
                            obj = NonConvexObject(
                                self.space,
                                x, y,
                                shape_info["color"],
                                self.selected_shape_type,
                                shape_info["mass"]
                            )
                            self.non_convex_objects.append(obj)
                        elif self.selected_shape_type in self.custom_meshes:
                            # カスタムメッシュ
                            custom_mesh = self.custom_meshes[self.selected_shape_type]
                            # 画像の位置を考慮して座標を調整
                            # クリック位置は画面座標なので、画像の位置を考慮する必要がある
                            # ただし、メッシュは既に1/5スケールで読み込まれているので、
                            # クリック位置をそのまま使用（画像の位置は表示用のみ）
                            obj = NonConvexObject(
                                self.space,
                                x, y,
                                (255, 100, 100),  # デフォルト色
                                "custom",
                                ANIMAL_MASS * 2,
                                custom_mesh
                            )
                            self.non_convex_objects.append(obj)
            
            # キーボードで動物タイプを切り替え
            elif event.type == pygame.KEYDOWN:
                # 数字キーで選択（1-9まで対応）
                key_to_index = {
                    pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                    pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
                    pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8
                }
                
                if event.key in key_to_index:
                    index = key_to_index[event.key]
                    if self.mode == "animal":
                        if index < len(self.animal_types):
                            self.selected_animal_type = self.animal_types[index]
                    else:
                        if index < len(self.shape_types):
                            self.selected_shape_type = self.shape_types[index]
                elif event.key == pygame.K_m:
                    # モード切り替え（動物 <-> 非凸物体）
                    self.mode = "non_convex" if self.mode == "animal" else "animal"
                elif event.key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
                    # カスタムメッシュを読み込み
                    self.load_custom_mesh()
                elif event.key == pygame.K_r:
                    # リセット：すべてのオブジェクトを削除
                    for animal in self.animals:
                        animal.remove()
                    self.animals.clear()
                    for obj in self.non_convex_objects:
                        obj.remove()
                    self.non_convex_objects.clear()
        
        return True
    
    def update(self):
        """ゲームの状態を更新"""
        # 物理エンジンの更新
        dt = 1.0 / FPS
        self.space.step(dt)
        
        # 画面外に出た動物を削除
        animals_to_remove = []
        for animal in self.animals:
            x, y = animal.body.position
            if y > SCREEN_HEIGHT + 100 or x < -100 or x > SCREEN_WIDTH + 100:
                animals_to_remove.append(animal)
        
        for animal in animals_to_remove:
            animal.remove()
            self.animals.remove(animal)
        
        # 画面外に出た非凸物体を削除
        objects_to_remove = []
        for obj in self.non_convex_objects:
            x, y = obj.body.position
            if y > SCREEN_HEIGHT + 100 or x < -100 or x > SCREEN_WIDTH + 100:
                objects_to_remove.append(obj)
        
        for obj in objects_to_remove:
            obj.remove()
            self.non_convex_objects.remove(obj)
    
    def draw(self):
        """画面を描画"""
        # 背景をクリア
        self.screen.fill((135, 206, 235))  # 空色
        
        # カスタムメッシュの画像を背景として表示
        if self.mode == "non_convex" and self.selected_shape_type in self.custom_mesh_images:
            image_path = self.custom_mesh_images[self.selected_shape_type]
            try:
                bg_image = pygame.image.load(image_path)
                # 画像を1/5のサイズにスケール
                img_width, img_height = bg_image.get_size()
                scaled_width = int(img_width * self.custom_mesh_scale)
                scaled_height = int(img_height * self.custom_mesh_scale)
                bg_image = pygame.transform.scale(bg_image, (scaled_width, scaled_height))
                # 画像を表示
                self.screen.blit(bg_image, self.custom_mesh_image_pos)
            except Exception as e:
                print(f"画像の読み込みに失敗しました: {e}")
        
        # 地面を描画
        pygame.draw.rect(
            self.screen,
            GREEN,
            (0, GROUND_Y, SCREEN_WIDTH, GROUND_HEIGHT)
        )
        
        # 動物を描画
        for animal in self.animals:
            animal.draw(self.screen)
        
        # 非凸物体を描画
        for obj in self.non_convex_objects:
            obj.draw(self.screen)
        
        # UI情報を表示
        font = pygame.font.Font(None, 36)
        mode_text = "動物モード" if self.mode == "animal" else "非凸物体モード"
        info_text = f"モード: {mode_text} (Mで切り替え, Rでリセット)"
        text_surface = font.render(info_text, True, BLACK)
        self.screen.blit(text_surface, (10, 10))
        
        if self.mode == "animal":
            # 動物の種類リストを表示
            y_offset = 50
            for i, animal_type in enumerate(self.animal_types):
                color = ANIMALS[animal_type]["color"]
                marker = ">" if animal_type == self.selected_animal_type else " "
                text = f"{marker} {i+1}: {animal_type}"
                text_surface = font.render(text, True, color)
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 30
        else:
            # 非凸物体の種類リストを表示
            y_offset = 50
            for i, shape_type in enumerate(self.shape_types):
                if shape_type in NON_CONVEX_SHAPES:
                    color = NON_CONVEX_SHAPES[shape_type]["color"]
                elif shape_type in self.custom_meshes:
                    color = (255, 100, 100)  # カスタムメッシュのデフォルト色
                else:
                    color = (200, 200, 200)  # その他の色
                marker = ">" if shape_type == self.selected_shape_type else " "
                # キー番号を表示（1-9まで）
                key_num = i + 1 if i < 9 else "?"
                text = f"{marker} {key_num}: {shape_type}"
                text_surface = font.render(text, True, color)
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 30
        
        pygame.display.flip()
    
    def run(self):
        """ゲームのメインループ"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def load_custom_mesh(self, filename="mesh.json"):
        """カスタムメッシュを読み込み"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                mesh_data = json.load(f)
            
            # メッシュ定義を取得
            from mesh_editor import ShapePlacement
            shapes = [ShapePlacement.from_dict(s) for s in mesh_data.get("shapes", [])]
            
            # メッシュ定義を作成（1/5スケールで、座標を調整）
            mesh_definitions = []
            scale = self.custom_mesh_scale  # 1/5
            
            for shape in shapes:
                # 三角分割されたポリゴンのみを処理
                if shape.shape_type == "triangulated_polygon" and hasattr(shape, 'triangles') and shape.triangles:
                    for triangle in shape.triangles:
                        # 相対座標を絶対座標に変換し、1/5スケールを適用
                        abs_triangle = [
                            ((shape.x + v[0]) * scale, (shape.y + v[1]) * scale)
                            for v in triangle
                        ]
                        mesh_definitions.append({
                            "type": "poly",
                            "vertices": abs_triangle
                        })
            
            # カスタムメッシュとして登録
            # ファイル名から拡張子を除去してメッシュ名を取得
            import os
            mesh_name = os.path.splitext(os.path.basename(filename))[0]
            if mesh_name == "mesh":
                mesh_name = "custom_mesh"  # デフォルト名を変更
            
            self.custom_meshes[mesh_name] = mesh_definitions
            
            # 画像パスを保存
            if "background_image" in mesh_data and mesh_data["background_image"]:
                self.custom_mesh_images[mesh_name] = mesh_data["background_image"]
            
            # 形状タイプリストに追加（まだ追加されていない場合のみ）
            if mesh_name not in self.shape_types:
                self.shape_types.append(mesh_name)
                print(f"カスタムメッシュ '{mesh_name}' を形状リストに追加しました")
            
            print(f"カスタムメッシュを読み込みました: {filename} (名前: {mesh_name}, 形状数: {len(mesh_definitions)}, スケール: {scale})")
            return True
        except Exception as e:
            print(f"カスタムメッシュの読み込みに失敗しました: {e}")
            return False

