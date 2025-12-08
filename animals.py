"""
動物のクラス定義
すべての座標はスケール済み（ゲーム座標系）で統一
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
    
    すべての座標はスケール済み（ゲーム座標系）で統一されています。
    mesh_centerとメッシュの三角形は同じスケールの座標系を使用します。
    """
    
    DEFAULT_SCALE = 0.15  # デフォルトスケール
    
    def __init__(self, space, x, y, color, mesh_definitions, mass=None, 
                 texture_path=None, mesh_center=(0, 0), scaled_image_size=None, 
                 scale=None, physics_enabled=True):
        """
        非凸物体を初期化
        
        Args:
            space: pymunkの物理空間
            x, y: 初期位置（ゲーム座標）
            color: 色
            mesh_definitions: 三角形メッシュ定義（スケール済み絶対座標）
            mass: 質量
            texture_path: テクスチャ画像のパス
            mesh_center: メッシュの重心（スケール済み座標）
            scaled_image_size: スケール済み画像サイズ (width, height)
            scale: メッシュのスケール値
            physics_enabled: 物理エンジンを有効にするか
        """
        self.space = space
        self.color = color
        self.texture_path = texture_path
        self.mesh_center = mesh_center  # スケール済み座標での重心
        self.scaled_image_size = scaled_image_size
        self.scale = scale if scale is not None else self.DEFAULT_SCALE
        self._physics_enabled = False
        
        # テクスチャ画像を読み込み（スケール済みサイズで保持）
        self.texture_image = None
        if texture_path:
            try:
                original_img = pygame.image.load(texture_path)
                # スケール済みサイズに変換
                if scaled_image_size:
                    self.texture_image = pygame.transform.scale(
                        original_img, scaled_image_size
                    )
                else:
                    # scaled_image_sizeがない場合は自動計算
                    orig_w, orig_h = original_img.get_size()
                    scaled_w = int(orig_w * self.scale)
                    scaled_h = int(orig_h * self.scale)
                    self.texture_image = pygame.transform.scale(
                        original_img, (scaled_w, scaled_h)
                    )
                    self.scaled_image_size = (scaled_w, scaled_h)
            except Exception as e:
                print(f"テクスチャの読み込みに失敗しました: {e}")
        
        # 質量を決定
        if mass is None:
            mass = ANIMAL_MASS * 2
        self.mass = mass
        
        # メッシュ定義を相対座標に変換（重心を原点に）
        # mesh_centerを基準にする
        if mesh_definitions and self.mesh_center:
            cx, cy = self.mesh_center
            for mesh_def in mesh_definitions:
                if mesh_def["type"] == "poly":
                    mesh_def["vertices"] = [
                        (vx - cx, vy - cy) for vx, vy in mesh_def["vertices"]
                    ]
        
        # 物理ボディの作成
        def calculate_triangle_area(vertices):
            if len(vertices) != 3:
                return 0
            return abs(
                (vertices[0][0] * (vertices[1][1] - vertices[2][1]) +
                 vertices[1][0] * (vertices[2][1] - vertices[0][1]) +
                 vertices[2][0] * (vertices[0][1] - vertices[1][1])) / 2.0
            )
        
        # 各三角形の面積と慣性モーメントを計算
        triangle_areas = []
        total_area = 0
        for mesh_def in mesh_definitions:
            if mesh_def["type"] == "poly":
                area = calculate_triangle_area(mesh_def["vertices"])
                triangle_areas.append(area)
                total_area += area
        
        total_moment = 0
        if total_area > 0:
            for i, mesh_def in enumerate(mesh_definitions):
                if mesh_def["type"] == "poly":
                    triangle_mass = mass * (triangle_areas[i] / total_area)
                    vertices = mesh_def["vertices"]
                    moment = pymunk.moment_for_poly(triangle_mass, vertices, (0, 0))
                    total_moment += moment
        else:
            total_moment = pymunk.moment_for_box(mass, (ANIMAL_SIZE * 1.5, ANIMAL_SIZE * 1.5))
        
        self.body = pymunk.Body(mass, total_moment)
        self.body.position = x, y
        
        # 各三角形を物理シェイプとして作成
        self.shapes = []
        for mesh_def in mesh_definitions:
            if mesh_def["type"] == "poly":
                vertices = mesh_def["vertices"]
                shape = pymunk.Poly(self.body, vertices)
                shape.friction = 15.0
                shape.elasticity = 0.3
                self.shapes.append(shape)
        
        self.mesh_definitions = mesh_definitions
        
        if physics_enabled:
            self.enable_physics()
        else:
            self.disable_physics()
    
    def enable_physics(self):
        """物理エンジンを有効にする"""
        if not self._physics_enabled:
            if self.body not in self.space.bodies:
                self.space.add(self.body)
            for shape in self.shapes:
                if shape not in self.space.shapes:
                    self.space.add(shape)
            self._physics_enabled = True
    
    def disable_physics(self):
        """物理エンジンを無効にする"""
        if self._physics_enabled:
            for shape in self.shapes:
                if shape in self.space.shapes:
                    self.space.remove(shape)
            if self.body in self.space.bodies:
                self.space.remove(self.body)
            self._physics_enabled = False
    
    def is_physics_enabled(self):
        return self._physics_enabled
    
    def set_position(self, x, y):
        self.body.position = x, y
    
    def get_position(self):
        return self.body.position
    
    def set_angle(self, angle):
        self.body.angle = angle
    
    def set_angle_degrees(self, angle_degrees):
        self.body.angle = math.radians(angle_degrees)
    
    def get_angle(self):
        return self.body.angle
    
    def get_angle_degrees(self):
        return math.degrees(self.body.angle)
    
    def set_velocity(self, vx, vy):
        if self._physics_enabled:
            self.body.velocity = vx, vy
    
    def get_velocity(self):
        if self._physics_enabled:
            return self.body.velocity
        return (0, 0)
    
    def set_angular_velocity(self, angular_velocity):
        if self._physics_enabled:
            self.body.angular_velocity = angular_velocity
    
    def get_angular_velocity(self):
        if self._physics_enabled:
            return self.body.angular_velocity
        return 0
    
    @classmethod
    def create(cls, space, x, y, mesh_definitions, color=(255, 100, 100), 
               mass=None, texture_path=None, mesh_center=(0, 0), 
               scaled_image_size=None, scale=None, physics_enabled=True):
        """オブジェクトを生成する便利メソッド"""
        return cls(
            space=space,
            x=x,
            y=y,
            color=color,
            mesh_definitions=mesh_definitions,
            mass=mass,
            texture_path=texture_path,
            mesh_center=mesh_center,
            scaled_image_size=scaled_image_size,
            scale=scale,
            physics_enabled=physics_enabled
        )
    
    def draw(self, screen):
        """非凸物体を描画"""
        body_pos = self.body.position
        body_angle = self.body.angle
        
        # テクスチャ画像がある場合は画像を描画
        if self.texture_image and self.scaled_image_size:
            img_w, img_h = self.scaled_image_size
            
            # 回転を適用
            rotated_image = pygame.transform.rotate(self.texture_image, -math.degrees(body_angle))
            rot_width, rot_height = rotated_image.get_size()
            
            # 画像中心からメッシュ重心へのオフセット（スケール済み座標）
            # mesh_centerはスケール済み座標、画像中心は(img_w/2, img_h/2)
            image_center_x = img_w / 2.0
            image_center_y = img_h / 2.0
            
            offset_x = self.mesh_center[0] - image_center_x
            offset_y = self.mesh_center[1] - image_center_y
            
            # 回転を適用
            cos_a = math.cos(body_angle)
            sin_a = math.sin(body_angle)
            rotated_offset_x = offset_x * cos_a - offset_y * sin_a
            rotated_offset_y = offset_x * sin_a + offset_y * cos_a
            
            # 描画位置: body_posはメッシュ重心の位置
            # 画像の中心がbody_pos - offset（メッシュ重心から画像中心へ戻す）に来るようにする
            draw_x = int(body_pos.x - rot_width // 2 - rotated_offset_x)
            draw_y = int(body_pos.y - rot_height // 2 - rotated_offset_y)
            
            screen.blit(rotated_image, (draw_x, draw_y))
        
        # ワイヤーフレーム描画（デバッグ用）- ボーン表示を無効化
        # テクスチャがない場合のみポリゴンを描画（エッジなし）
        if not self.texture_image:
            for mesh_def in self.mesh_definitions:
                if mesh_def["type"] == "poly":
                    vertices = mesh_def["vertices"]
                    world_vertices = []
                    for vx, vy in vertices:
                        cos_a = math.cos(body_angle)
                        sin_a = math.sin(body_angle)
                        rotated_x = vx * cos_a - vy * sin_a
                        rotated_y = vx * sin_a + vy * cos_a
                        world_x = int(body_pos.x + rotated_x)
                        world_y = int(body_pos.y + rotated_y)
                        world_vertices.append((world_x, world_y))
                    
                    if len(world_vertices) == 3:
                        pygame.draw.polygon(screen, self.color, world_vertices)
    
    def remove(self):
        """物理空間から削除"""
        if self._physics_enabled:
            self.disable_physics()
