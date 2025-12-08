"""
動物のクラス定義
"""
import pymunk
import pygame
import math
from config import (
    ANIMAL_SIZE, ANIMAL_MASS, 
    ORANGE, YELLOW, WHITE, BLUE, BLACK
)





class NonConvexObject:
    """非凸の剛体物体クラス（三角形メッシュのみ）
    
    物理エンジンのON/OFF、位置・角度の変更、オブジェクト生成などの機能を提供します。
    
    使用例:
        # オブジェクトを生成
        obj = NonConvexObject.create(
            space=space,
            x=100, y=100,
            mesh_definitions=mesh_defs,
            texture_path="texture.png",
            physics_enabled=True
        )
        
        # 物理エンジンをOFFにする
        obj.disable_physics()
        
        # 位置を変更
        obj.set_position(200, 300)
        
        # 角度を変更（度）
        obj.set_angle_degrees(45)
        
        # 物理エンジンをONにする
        obj.enable_physics()
        
        # 位置を取得
        x, y = obj.get_position()
        
        # 角度を取得（度）
        angle = obj.get_angle_degrees()
    """
    
    def __init__(self, space, x, y, color, mesh_definitions, mass=None, texture_path=None, original_triangles=None, mesh_center=(0, 0), image_size=None, physics_enabled=True):
        """
        非凸物体を初期化（三角形メッシュのみ）
        
        Args:
            space: pymunkの物理空間
            x, y: 初期位置
            color: 色
            mesh_definitions: 三角形メッシュ定義のリスト（各要素は {"type": "poly", "vertices": [(x1, y1), (x2, y2), (x3, y3)]}）
            mass: 質量（Noneの場合はANIMAL_MASS * 2を使用）
            texture_path: テクスチャ画像のパス
            original_triangles: 元の画像座標系での三角形リスト（未使用、後方互換性のため）
            mesh_center: 画像座標系でのメッシュの重心位置
            image_size: 画像サイズ (width, height)
            physics_enabled: 物理エンジンを有効にするかどうか（デフォルト: True）
        """
        self.space = space
        self.color = color
        self.texture_path = texture_path
        self.mesh_center = mesh_center  # 画像座標系でのメッシュの重心位置
        self.image_size = image_size  # 画像サイズ
        self._physics_enabled = False  # 初期化時はFalse、後で設定
        
        # テクスチャ画像を読み込み
        self.texture_image = None
        if texture_path:
            try:
                self.texture_image = pygame.image.load(texture_path)
            except Exception as e:
                print(f"テクスチャの読み込みに失敗しました: {e}")
        
        # 質量を決定
        if mass is None:
            mass = ANIMAL_MASS * 2
        self.mass = mass
        
        # メッシュ定義を相対座標に変換（重心を原点に）
        if mesh_definitions:
            # すべての三角形の頂点から重心を計算
            all_points = []
            for mesh_def in mesh_definitions:
                if mesh_def["type"] == "poly":
                    all_points.extend(mesh_def["vertices"])
            
            if all_points:
                cx = sum(p[0] for p in all_points) / len(all_points)
                cy = sum(p[1] for p in all_points) / len(all_points)
                # 座標を相対座標に変換
                for mesh_def in mesh_definitions:
                    if mesh_def["type"] == "poly":
                        mesh_def["vertices"] = [(vx - cx, vy - cy) for vx, vy in mesh_def["vertices"]]
        
        # 物理ボディの作成
        # 各三角形の面積を計算して、質量を面積比で分配し、慣性モーメントを合成
        def calculate_triangle_area(vertices):
            """三角形の面積を計算（Shoelace formula）"""
            if len(vertices) != 3:
                return 0
            area = abs(
                (vertices[0][0] * (vertices[1][1] - vertices[2][1]) +
                 vertices[1][0] * (vertices[2][1] - vertices[0][1]) +
                 vertices[2][0] * (vertices[0][1] - vertices[1][1])) / 2.0
            )
            return area
        
        # 各三角形の面積を計算
        triangle_areas = []
        total_area = 0
        for mesh_def in mesh_definitions:
            if mesh_def["type"] == "poly":
                area = calculate_triangle_area(mesh_def["vertices"])
                triangle_areas.append(area)
                total_area += area
        
        # 各三角形の慣性モーメントを計算して合成
        total_moment = 0
        if total_area > 0:
            for i, mesh_def in enumerate(mesh_definitions):
                if mesh_def["type"] == "poly":
                    triangle_mass = mass * (triangle_areas[i] / total_area)
                    vertices = mesh_def["vertices"]
                    moment = pymunk.moment_for_poly(triangle_mass, vertices, (0, 0))
                    total_moment += moment
        else:
            # フォールバック：デフォルトの慣性モーメント
            total_moment = pymunk.moment_for_box(mass, (ANIMAL_SIZE * 1.5, ANIMAL_SIZE * 1.5))
        
        self.body = pymunk.Body(mass, total_moment)
        self.body.position = x, y
        
        # 各三角形を物理シェイプとして作成
        self.shapes = []
        for mesh_def in mesh_definitions:
            if mesh_def["type"] == "poly":
                vertices = mesh_def["vertices"]
                shape = pymunk.Poly(self.body, vertices)
                shape.friction = 15.0  # 摩擦を強く設定
                shape.elasticity = 0.3
                self.shapes.append(shape)
        
        # 描画用のメッシュ定義を保存
        self.mesh_definitions = mesh_definitions
        
        # 物理エンジンの初期状態を設定
        if physics_enabled:
            self.enable_physics()
        else:
            self.disable_physics()
    
    def enable_physics(self):
        """物理エンジンを有効にする"""
        if not self._physics_enabled:
            # BodyをSpaceに追加
            if self.body not in self.space.bodies:
                self.space.add(self.body)
            # 各ShapeをSpaceに追加
            for shape in self.shapes:
                if shape not in self.space.shapes:
                    self.space.add(shape)
            self._physics_enabled = True
    
    def disable_physics(self):
        """物理エンジンを無効にする（描画は継続）"""
        if self._physics_enabled:
            # 各ShapeをSpaceから削除
            for shape in self.shapes:
                if shape in self.space.shapes:
                    self.space.remove(shape)
            # BodyをSpaceから削除
            if self.body in self.space.bodies:
                self.space.remove(self.body)
            self._physics_enabled = False
    
    def is_physics_enabled(self):
        """物理エンジンが有効かどうかを返す"""
        return self._physics_enabled
    
    def set_position(self, x, y):
        """オブジェクトの位置を設定"""
        self.body.position = x, y
    
    def get_position(self):
        """オブジェクトの位置を取得"""
        return self.body.position
    
    def set_angle(self, angle):
        """オブジェクトの角度を設定（ラジアン）"""
        self.body.angle = angle
    
    def set_angle_degrees(self, angle_degrees):
        """オブジェクトの角度を設定（度）"""
        self.body.angle = math.radians(angle_degrees)
    
    def get_angle(self):
        """オブジェクトの角度を取得（ラジアン）"""
        return self.body.angle
    
    def get_angle_degrees(self):
        """オブジェクトの角度を取得（度）"""
        return math.degrees(self.body.angle)
    
    def set_velocity(self, vx, vy):
        """オブジェクトの速度を設定"""
        if self._physics_enabled:
            self.body.velocity = vx, vy
    
    def get_velocity(self):
        """オブジェクトの速度を取得"""
        if self._physics_enabled:
            return self.body.velocity
        return (0, 0)
    
    def set_angular_velocity(self, angular_velocity):
        """オブジェクトの角速度を設定"""
        if self._physics_enabled:
            self.body.angular_velocity = angular_velocity
    
    def get_angular_velocity(self):
        """オブジェクトの角速度を取得"""
        if self._physics_enabled:
            return self.body.angular_velocity
        return 0
    
    @classmethod
    def create(cls, space, x, y, mesh_definitions, color=(255, 100, 100), mass=None, texture_path=None, mesh_center=(0, 0), image_size=None, physics_enabled=True):
        """
        オブジェクトを生成する便利メソッド
        
        Args:
            space: pymunkの物理空間
            x, y: 初期位置
            mesh_definitions: 三角形メッシュ定義のリスト
            color: 色（デフォルト: (255, 100, 100)）
            mass: 質量（Noneの場合はANIMAL_MASS * 2を使用）
            texture_path: テクスチャ画像のパス
            mesh_center: 画像座標系でのメッシュの重心位置
            image_size: 画像サイズ (width, height)
            physics_enabled: 物理エンジンを有効にするかどうか（デフォルト: True）
        
        Returns:
            NonConvexObject: 生成されたオブジェクト
        """
        return cls(
            space=space,
            x=x,
            y=y,
            color=color,
            mesh_definitions=mesh_definitions,
            mass=mass,
            texture_path=texture_path,
            mesh_center=mesh_center,
            image_size=image_size,
            physics_enabled=physics_enabled
        )
    
    def draw(self, screen):
        """非凸物体を描画（テクスチャ画像がある場合は画像を描画）"""
        # ボディの位置と回転を取得
        body_pos = self.body.position
        body_angle = self.body.angle
        
        # テクスチャ画像がある場合は画像を描画
        if self.texture_image:
            # 画像のサイズを取得
            img_width, img_height = self.texture_image.get_size()
            
            # メッシュのスケール（0.2 = 1/5）を適用
            mesh_scale = 0.2
            scaled_width = int(img_width * mesh_scale)
            scaled_height = int(img_height * mesh_scale)
            
            # 画像をスケール
            scaled_image = pygame.transform.scale(self.texture_image, (scaled_width, scaled_height))
            
            # 回転を適用
            rotated_image = pygame.transform.rotate(scaled_image, -math.degrees(body_angle))
            
            # 回転後の画像サイズを取得（回転でサイズが変わるため）
            rot_width, rot_height = rotated_image.get_size()
            
            # メッシュの重心位置から画像中心へのオフセットを計算
            # mesh_centerは画像座標系（左上が原点）での絶対座標
            # 画像中心は (img_w/2, img_h/2)
            if self.image_size and self.mesh_center:
                img_w, img_h = self.image_size
                image_center_x = img_w / 2.0
                image_center_y = img_h / 2.0
                # 画像中心からのメッシュ重心のオフセット（画像座標系）
                offset_x = self.mesh_center[0] - image_center_x
                offset_y = self.mesh_center[1] - image_center_y
                # スケールを適用（ゲーム座標系に変換）
                offset_x *= mesh_scale
                offset_y *= mesh_scale
                # 回転を適用
                cos_a = math.cos(body_angle)
                sin_a = math.sin(body_angle)
                rotated_offset_x = offset_x * cos_a - offset_y * sin_a
                rotated_offset_y = offset_x * sin_a + offset_y * cos_a
            else:
                rotated_offset_x = 0
                rotated_offset_y = 0
            
            # 画像の中心をオブジェクトの位置に合わせ、メッシュ重心のオフセットを考慮
            draw_x = int(body_pos.x - rot_width // 2 + rotated_offset_x)
            draw_y = int(body_pos.y - rot_height // 2 + rotated_offset_y)
            
            # 画像を描画
            screen.blit(rotated_image, (draw_x, draw_y))
        
        # 各三角形を描画（デバッグ用のワイヤーフレーム、必要に応じてコメントアウト可能）
        for mesh_def in self.mesh_definitions:
            if mesh_def["type"] == "poly":
                vertices = mesh_def["vertices"]
                # ローカル座標をワールド座標に変換
                world_vertices = []
                for vx, vy in vertices:
                    # 回転を適用
                    cos_a = math.cos(body_angle)
                    sin_a = math.sin(body_angle)
                    rotated_x = vx * cos_a - vy * sin_a
                    rotated_y = vx * sin_a + vy * cos_a
                    # 平行移動を適用
                    world_x = int(body_pos.x + rotated_x)
                    world_y = int(body_pos.y + rotated_y)
                    world_vertices.append((world_x, world_y))
                
                # 三角形を描画（ワイヤーフレームのみ、テクスチャがある場合は薄く表示）
                if len(world_vertices) == 3:
                    if self.texture_image:
                        # テクスチャがある場合はワイヤーフレームのみ（薄く）
                        pygame.draw.polygon(screen, (100, 100, 100), world_vertices, 1)
                    else:
                        # テクスチャがない場合は通常通り
                        pygame.draw.polygon(screen, self.color, world_vertices)
                        pygame.draw.polygon(screen, BLACK, world_vertices, 2)
    
    def remove(self):
        """物理空間から非凸物体を削除"""
        # 物理エンジンが有効な場合は無効にしてから削除
        if self._physics_enabled:
            self.disable_physics()
