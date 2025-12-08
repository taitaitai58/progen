"""
NonConvexObjectの機能をテストするゲーム
物理エンジンのON/OFF、位置・角度の変更、オブジェクト生成などをテストできます
"""
import pygame
import pymunk
import os
import json
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRAVITY, FPS,
    GROUND_HEIGHT, GROUND_Y, BLACK, GREEN, WHITE, RED, YELLOW, BLUE,
    get_japanese_font
)
from animals import NonConvexObject
from mesh_editor import TriangleMesh


class TestGame:
    """NonConvexObjectの機能をテストするゲーム"""
    
    def __init__(self):
        """ゲームを初期化"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("NonConvexObject テストゲーム")
        self.clock = pygame.time.Clock()
        
        # 物理空間の作成
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        
        # オブジェクトのリスト
        self.objects = []
        self.selected_object_index = -1  # 選択中のオブジェクトのインデックス
        
        # 地面の作成
        self.create_ground()
        
        # メッシュの読み込み
        self.mesh_definitions = []
        self.texture_path = None
        self.mesh_center = (0, 0)
        self.image_size = None
        self.load_default_mesh()
        
        # 操作モード
        self.control_mode = "physics"  # "physics" or "manual"
        self.move_speed = 5.0
        self.rotate_speed = 5.0  # 度/フレーム

        # ゲームオーバー判定
        self.game_over = False


    
    def create_ground(self):
        """地面を作成"""
        # 地面のボディ（静的）
        ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        ground_shape = pymunk.Segment(
            ground_body,
            (SCREEN_WIDTH/4, GROUND_Y),
            (3*SCREEN_WIDTH/4, GROUND_Y),
            5
        )
        ground_shape.friction = 1.0
        self.space.add(ground_body, ground_shape)
        
       
    
    def load_default_mesh(self):
        """デフォルトのメッシュを読み込み"""
        mesh_folder = "meshes/mesh1"
        mesh_json = os.path.join(mesh_folder, "mesh.json")
        
        if os.path.exists(mesh_json):
            try:
                with open(mesh_json, 'r', encoding='utf-8') as f:
                    mesh_data = json.load(f)
                
                # メッシュ定義を取得
                meshes = [TriangleMesh.from_dict(s) for s in mesh_data.get("shapes", [])]
                
                # 画像パスを取得
                image_path = None
                if "background_image" in mesh_data and mesh_data["background_image"]:
                    bg_img_path = mesh_data["background_image"]
                    if not os.path.isabs(bg_img_path):
                        image_path = os.path.join(mesh_folder, os.path.basename(bg_img_path))
                    else:
                        image_path = bg_img_path
                
                # 画像が見つからない場合、メッシュフォルダ内の画像ファイルを探す
                if not image_path or not os.path.exists(image_path):
                    for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                        for file in os.listdir(mesh_folder):
                            if file.lower().endswith(ext) and file != os.path.basename(mesh_json):
                                image_path = os.path.join(mesh_folder, file)
                                break
                        if image_path and os.path.exists(image_path):
                            break
                
                if image_path and os.path.exists(image_path):
                    self.texture_path = image_path
                
                # 画像サイズを取得
                if image_path and os.path.exists(image_path):
                    try:
                        temp_img = pygame.image.load(image_path)
                        self.image_size = temp_img.get_size()
                    except:
                        pass
                
                # メッシュ定義を作成（1/5スケール）
                mesh_definitions = []
                scale = 0.2  # 1/5スケール
                
                # メッシュの重心位置を保存（画像座標系の絶対座標のまま）
                # mesh_centerは画像座標系（左上が原点）での絶対座標
                mesh_center_x = meshes[0].x if meshes else 0
                mesh_center_y = meshes[0].y if meshes else 0
                self.mesh_center = (mesh_center_x, mesh_center_y)
                
                for mesh in meshes:
                    for triangle in mesh.triangles:
                        abs_triangle = [
                            ((mesh.x + v[0]) * scale, (mesh.y + v[1]) * scale)
                            for v in triangle
                        ]
                        mesh_definitions.append({
                            "type": "poly",
                            "vertices": abs_triangle
                        })
                
                self.mesh_definitions = mesh_definitions
                print(f"メッシュを読み込みました: {len(mesh_definitions)}個の三角形")
            except Exception as e:
                print(f"メッシュの読み込みに失敗しました: {e}")
                # フォールバック：簡単な三角形を作成
                self.create_fallback_mesh()
        else:
            # フォールバック：簡単な三角形を作成
            self.create_fallback_mesh()
    
    def create_fallback_mesh(self):
        """フォールバック用の簡単なメッシュを作成"""
        size = 50
        self.mesh_definitions = [{
            "type": "poly",
            "vertices": [
                (0, -size),
                (-size * 0.866, size * 0.5),
                (size * 0.866, size * 0.5)
            ]
        }]
        self.mesh_center = (0, 0)
        self.image_size = None
        self.texture_path = None
    
    def create_object(self, x, y, physics_enabled=True):
        """オブジェクトを生成"""
        obj = NonConvexObject.create(
            space=self.space,
            x=x,
            y=y,
            mesh_definitions=self.mesh_definitions.copy(),
            color=(255, 100, 100),
            texture_path=self.texture_path,
            mesh_center=self.mesh_center,
            image_size=self.image_size,
            physics_enabled=physics_enabled
        )
        obj.is_ready_to_fall = False

        self.objects.append(obj)
        self.selected_object_index = len(self.objects) - 1
        return obj
    
        

    
    def get_selected_object(self):
        """選択中のオブジェクトを取得"""
        if 0 <= self.selected_object_index < len(self.objects):
            return self.objects[self.selected_object_index]
        return None
    
    def select_next_object(self):
        """次のオブジェクトを選択"""
        if len(self.objects) > 0:
            self.selected_object_index = (self.selected_object_index + 1) % len(self.objects)
        else:
            self.selected_object_index = -1
    
    def select_previous_object(self):
        """前のオブジェクトを選択"""
        if len(self.objects) > 0:
            self.selected_object_index = (self.selected_object_index - 1) % len(self.objects)
        else:
            self.selected_object_index = -1
    
    def handle_events(self):
        """イベントを処理"""
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos

                # ★ 古い操作中オブジェクトがあれば落下させる（これが強制落下）
                for o in self.objects:
                    if not o.is_ready_to_fall:
                        o.is_ready_to_fall = True
                        o.enable_physics()

                # ★ 新しいオブジェクト（物理OFF）を生成
                self.create_object(x, y, physics_enabled=False)

            
            elif event.type == pygame.KEYDOWN:
                obj = self.get_selected_object()               
                # オブジェクト選択
                if event.key == pygame.K_TAB:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.select_previous_object()
                    else:
                        self.select_next_object()
                
                elif event.key == pygame.K_SPACE:
                    obj = self.get_selected_object()
                    if obj:
                        obj.is_ready_to_fall = True
                        obj.enable_physics()
                        print("落下開始！")
                
                # 物理エンジンのON/OFF
                elif event.key == pygame.K_p:
                    if obj:
                        if obj.is_physics_enabled():
                            obj.disable_physics()
                            print("物理エンジンをOFFにしました")
                        else:
                            obj.enable_physics()
                            print("物理エンジンをONにしました")
                
                # オブジェクトの削除
                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    if obj and len(self.objects) > 0:
                        obj.remove()
                        self.objects.remove(obj)
                        if self.selected_object_index >= len(self.objects):
                            self.selected_object_index = len(self.objects) - 1
                        print("オブジェクトを削除しました")
                
                # 全削除
                elif event.key == pygame.K_r:
                    for obj in self.objects:
                        obj.remove()
                    self.objects.clear()
                    self.selected_object_index = -1
                    print("すべてのオブジェクトを削除しました")
                
                # 位置をリセット
                elif event.key == pygame.K_h:
                    if obj:
                        x, y = obj.get_position()
                        obj.set_position(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                        print(f"位置をリセットしました: ({SCREEN_WIDTH // 2}, {SCREEN_HEIGHT // 2})")
                
                # 角度をリセット
                elif event.key == pygame.K_0:
                    if obj:
                        obj.set_angle_degrees(0)
                        print("角度をリセットしました")
                
                
        
        # 連続入力の処理
        obj = self.get_selected_object()
        if obj:
            # 矢印キーで位置を変更
            if keys[pygame.K_LEFT]:
                x, y = obj.get_position()
                obj.set_position(x - self.move_speed, y)
            if keys[pygame.K_RIGHT]:
                x, y = obj.get_position()
                obj.set_position(x + self.move_speed, y)
            
            # Q/Eキーで角度を変更
            if keys[pygame.K_q]:
                angle = obj.get_angle_degrees()
                obj.set_angle_degrees(angle - self.rotate_speed)
            if keys[pygame.K_e]:
                angle = obj.get_angle_degrees()
                obj.set_angle_degrees(angle + self.rotate_speed)
            
            # W/A/S/Dキーで速度を設定（物理エンジンON時のみ）
            if obj.is_physics_enabled():
                if keys[pygame.K_w]:
                    obj.set_velocity(0, -500)
                if keys[pygame.K_s]:
                    obj.set_velocity(0, 500)
                if keys[pygame.K_a]:
                    obj.set_velocity(-500, 0)
                if keys[pygame.K_d]:
                    obj.set_velocity(500, 0)
        
        return True
    
    def update(self):
        """ゲームの状態を更新"""
        # 物理エンジンの更新
        dt = 1.0 / FPS
        self.space.step(dt)
        
        # 画面外に出たオブジェクトを削除
        objects_to_remove = []
        for obj in self.objects:
            x, y = obj.get_position()
            if y > SCREEN_HEIGHT + 200 or x < -200 or x > SCREEN_WIDTH + 200:
                objects_to_remove.append(obj)
        
        for obj in objects_to_remove:
            obj.remove()
            self.objects.remove(obj)
            if self.selected_object_index >= len(self.objects):
                self.selected_object_index = len(self.objects) - 1
        
        for obj in self.objects:
            if not obj.is_ready_to_fall:
            # ← このフラグが False の間は空中に固定
                obj.set_velocity(0, 0)
                obj.set_angular_velocity(0)
                continue

    
        if self.game_over:
             return  # ゲームオーバー時は何もしない

        dt = 1.0 / FPS
        self.space.step(dt)

        margin = 50

        for obj in self.objects:
            x, y = obj.get_position()
            if (x < -margin or x > SCREEN_WIDTH + margin or
                y < -margin or y > SCREEN_HEIGHT + margin):
                self.game_over = True   # ← ゲームオーバー！
                print("GAME OVER!")
                break
    
    def draw(self):
        """画面を描画"""
        # 背景をクリア
        self.screen.fill((135, 206, 235))  # 空色
        
        # 地面を描画
        pygame.draw.rect(
            self.screen,
            GREEN,
            (SCREEN_WIDTH/4, GROUND_Y, SCREEN_WIDTH/2, GROUND_HEIGHT)
        )
        
        # オブジェクトを描画
        for i, obj in enumerate(self.objects):
            obj.draw(self.screen)
            
            # 選択中のオブジェクトにマーカーを表示
            if i == self.selected_object_index:
                x, y = obj.get_position()
                # 円で囲む
                pygame.draw.circle(self.screen, YELLOW, (int(x), int(y)), 30, 3)
                # 物理エンジンの状態を表示
                if obj.is_physics_enabled():
                    pygame.draw.circle(self.screen, GREEN, (int(x), int(y)), 5)
                else:
                    pygame.draw.circle(self.screen, RED, (int(x), int(y)), 5)
        
        # UI情報を表示
        self.draw_ui()
        
        if self.game_over:
            font = get_japanese_font(60)
            text = font.render("GAME OVER", True, RED)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 30))

        pygame.display.flip()
    
    def get_controlled_object(self):
        for obj in self.objects:
            if not obj.is_ready_to_fall:
                return obj
        return None

       

    
    def draw_ui(self):
        """UIを描画"""
        font = get_japanese_font(24)
        small_font = get_japanese_font(20)
        
        y_offset = 10
        
        # タイトル
        title = "NonConvexObject テストゲーム"
        text_surface = font.render(title, True, BLACK)
        self.screen.blit(text_surface, (10, y_offset))
        y_offset += 30
        
        # 選択中のオブジェクト情報
        obj = self.get_selected_object()
        if obj:
            x, y = obj.get_position()
            angle = obj.get_angle_degrees()
            physics_status = "ON" if obj.is_physics_enabled() else "OFF"
            
            info_texts = [
                f"選択中のオブジェクト: {self.selected_object_index + 1}/{len(self.objects)}",
                f"位置: ({int(x)}, {int(y)})",
                f"角度: {int(angle)}°",
                f"物理エンジン: {physics_status}",
            ]
            
            for text in info_texts:
                text_surface = small_font.render(text, True, BLACK)
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25
        else:
            text = "オブジェクトが選択されていません"
            text_surface = small_font.render(text, True, RED)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        y_offset += 10
        
        # 操作説明
        instructions = [
            "=== 操作説明 ===",
            "左クリック: 物理エンジンONでオブジェクト生成",
            "右クリック: 物理エンジンOFFでオブジェクト生成",
            "Tab: 次のオブジェクトを選択",
            "Shift+Tab: 前のオブジェクトを選択",
            "P: 物理エンジンのON/OFF切り替え",
            "矢印キー: 位置を移動",
            "Q/E: 角度を回転",
            "W/A/S/D: 速度を設定（物理ON時のみ）",
            "H: 位置をリセット（画面中央）",
            "0: 角度をリセット",
            "Delete/Backspace: 選択中のオブジェクトを削除",
            "R: すべてのオブジェクトを削除",
        ]
        
        for instruction in instructions:
            text_surface = small_font.render(instruction, True, BLACK)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 22
        
        # オブジェクト数
        count_text = f"オブジェクト数: {len(self.objects)}"
        text_surface = font.render(count_text, True, BLACK)
        self.screen.blit(text_surface, (10, SCREEN_HEIGHT - 30))
    
    def run(self):
        """ゲームのメインループ"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = TestGame()
    game.run()

