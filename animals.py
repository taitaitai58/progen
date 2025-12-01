"""
動物のクラス定義
"""
import pymunk
import pygame
import math
from config import (
    ANIMAL_SIZE, ANIMAL_MASS, 
    ORANGE, YELLOW, WHITE, BLUE, BLACK, RED, PURPLE
)


class Animal:
    """動物の基本クラス"""
    
    def __init__(self, space, x, y, color, animal_type="default", mass=None):
        """
        動物を初期化
        
        Args:
            space: pymunkの物理空間
            x, y: 初期位置
            color: 色
            animal_type: 動物の種類
            mass: 質量（Noneの場合はANIMAL_MASSを使用）
        """
        self.space = space
        self.color = color
        self.animal_type = animal_type
        self.size = ANIMAL_SIZE
        
        # 質量を決定
        if mass is None:
            mass = ANIMAL_MASS
        
        # 物理ボディの作成（円形）
        moment = pymunk.moment_for_circle(mass, 0, self.size / 2)
        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        
        # 物理シェイプの作成
        self.shape = pymunk.Circle(self.body, self.size / 2)
        self.shape.friction = 0.7
        self.shape.elasticity = 0.3
        
        # 物理空間に追加
        space.add(self.body, self.shape)
    
    def draw(self, screen):
        """動物を描画"""
        x, y = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, (x, y), self.size // 2)
        pygame.draw.circle(screen, BLACK, (x, y), self.size // 2, 2)
    
    def remove(self):
        """物理空間から動物を削除"""
        self.space.remove(self.body, self.shape)


# 動物の種類を定義
ANIMALS = {
    "cat": {"color": ORANGE, "mass": ANIMAL_MASS},
    "dog": {"color": YELLOW, "mass": ANIMAL_MASS * 1.2},
    "rabbit": {"color": WHITE, "mass": ANIMAL_MASS * 0.8},
    "bear": {"color": (139, 69, 19), "mass": ANIMAL_MASS * 2},
    "bird": {"color": BLUE, "mass": ANIMAL_MASS * 0.6},
}


class NonConvexObject:
    """非凸の剛体物体クラス（複数の形状を結合したメッシュ）"""
    
    def __init__(self, space, x, y, color, shape_type="L", mass=None, custom_mesh=None):
        """
        非凸物体を初期化
        
        Args:
            space: pymunkの物理空間
            x, y: 初期位置
            color: 色
            shape_type: 形状の種類 ("L", "T", "U", "cross") または "custom"
            mass: 質量（Noneの場合はANIMAL_MASS * 2を使用）
            custom_mesh: カスタムメッシュ定義（shape_type="custom"の場合に使用）
        """
        self.space = space
        self.color = color
        self.shape_type = shape_type
        
        # 質量を決定
        if mass is None:
            mass = ANIMAL_MASS * 2
        
        # 形状の定義を取得
        if shape_type == "custom" and custom_mesh is not None:
            shape_definitions = custom_mesh
            # カスタムメッシュの場合は座標を相対座標に変換（重心を原点に）
            if shape_definitions:
                # すべての形状の重心を計算
                all_points = []
                for shape_def in shape_definitions:
                    if shape_def["type"] == "poly":
                        all_points.extend(shape_def["vertices"])
                    elif shape_def["type"] == "circle":
                        all_points.append(shape_def.get("offset", (0, 0)))
                
                if all_points:
                    cx = sum(p[0] for p in all_points) / len(all_points)
                    cy = sum(p[1] for p in all_points) / len(all_points)
                    # 座標を相対座標に変換
                    for shape_def in shape_definitions:
                        if shape_def["type"] == "poly":
                            shape_def["vertices"] = [(vx - cx, vy - cy) for vx, vy in shape_def["vertices"]]
                        elif shape_def["type"] == "circle":
                            offset = shape_def.get("offset", (0, 0))
                            shape_def["offset"] = (offset[0] - cx, offset[1] - cy)
        else:
            shape_definitions = self._get_shape_definitions(shape_type)
        
        # 物理ボディの作成
        # 複合形状の慣性モーメントを計算（ベストプラクティスに従う）
        # 各形状の面積を計算して、質量を面積比で分配し、慣性モーメントを合成
        def calculate_poly_area(vertices):
            """多角形の面積を計算（Shoelace formula）"""
            if len(vertices) < 3:
                return 0
            area = 0
            for i in range(len(vertices)):
                j = (i + 1) % len(vertices)
                area += vertices[i][0] * vertices[j][1]
                area -= vertices[j][0] * vertices[i][1]
            return abs(area) / 2.0
        
        # 各形状の面積を計算
        shape_areas = []
        total_area = 0
        for shape_def in shape_definitions:
            if shape_def["type"] == "poly":
                area = calculate_poly_area(shape_def["vertices"])
            elif shape_def["type"] == "circle":
                radius = shape_def["radius"]
                area = math.pi * radius * radius
            else:
                area = 0
            shape_areas.append(area)
            total_area += area
        
        # 各形状の慣性モーメントを計算して合成
        total_moment = 0
        if total_area > 0:
            for i, shape_def in enumerate(shape_definitions):
                shape_mass = mass * (shape_areas[i] / total_area)
                if shape_def["type"] == "poly":
                    vertices = shape_def["vertices"]
                    moment = pymunk.moment_for_poly(shape_mass, vertices, (0, 0))
                elif shape_def["type"] == "circle":
                    radius = shape_def["radius"]
                    moment = pymunk.moment_for_circle(shape_mass, 0, radius)
                else:
                    moment = 0
                total_moment += moment
        else:
            # フォールバック：デフォルトの慣性モーメント
            total_moment = pymunk.moment_for_box(mass, (ANIMAL_SIZE * 1.5, ANIMAL_SIZE * 1.5))
        
        self.body = pymunk.Body(mass, total_moment)
        self.body.position = x, y
        
        # Bodyを先にSpaceに追加（重要：Shapeを追加する前にBodyを追加する必要がある）
        space.add(self.body)
        
        # 複数の形状を作成して結合
        self.shapes = []
        for shape_def in shape_definitions:
            if shape_def["type"] == "poly":
                vertices = shape_def["vertices"]
                shape = pymunk.Poly(self.body, vertices)
            elif shape_def["type"] == "circle":
                offset = shape_def.get("offset", (0, 0))
                radius = shape_def["radius"]
                shape = pymunk.Circle(self.body, radius, offset)
            else:
                continue
            
            shape.friction = 0.7
            shape.elasticity = 0.3
            self.shapes.append(shape)
            space.add(shape)
        
        # 描画用の形状定義を保存
        self.shape_definitions = shape_definitions
    
    def _get_shape_definitions(self, shape_type):
        """
        形状タイプに応じた形状定義を返す
        
        Returns:
            形状定義のリスト（各要素は {"type": "poly"/"circle", ...}）
        """
        size = ANIMAL_SIZE * 1.5
        
        if shape_type == "L":
            # L字型（2つの矩形を結合）
            return [
                {
                    "type": "poly",
                    "vertices": [(-size, -size), (size, -size), (size, 0), (-size, 0)]
                },
                {
                    "type": "poly",
                    "vertices": [(-size, 0), (0, 0), (0, size), (-size, size)]
                }
            ]
        
        elif shape_type == "T":
            # T字型（3つの矩形を結合）
            return [
                {
                    "type": "poly",
                    "vertices": [(-size, -size), (size, -size), (size, 0), (-size, 0)]
                },
                {
                    "type": "poly",
                    "vertices": [(-size/2, 0), (size/2, 0), (size/2, size), (-size/2, size)]
                }
            ]
        
        elif shape_type == "U":
            # U字型（3つの矩形を結合）
            return [
                {
                    "type": "poly",
                    "vertices": [(-size, -size), (size, -size), (size, 0), (-size, 0)]
                },
                {
                    "type": "poly",
                    "vertices": [(-size, 0), (-size/2, 0), (-size/2, size), (-size, size)]
                },
                {
                    "type": "poly",
                    "vertices": [(size/2, 0), (size, 0), (size, size), (size/2, size)]
                }
            ]
        
        elif shape_type == "cross":
            # 十字型（4つの矩形を結合）
            half_size = size / 2
            return [
                {
                    "type": "poly",
                    "vertices": [(-half_size, -size), (half_size, -size), (half_size, -half_size), (-half_size, -half_size)]
                },
                {
                    "type": "poly",
                    "vertices": [(-size, -half_size), (size, -half_size), (size, half_size), (-size, half_size)]
                },
                {
                    "type": "poly",
                    "vertices": [(-half_size, half_size), (half_size, half_size), (half_size, size), (-half_size, size)]
                }
            ]
        
        elif shape_type == "star":
            # 星型（5つの三角形を結合）
            outer_radius = size
            inner_radius = size * 0.4
            vertices = []
            for i in range(10):
                angle = i * math.pi / 5
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                vertices.append((x, y))
            return [
                {
                    "type": "poly",
                    "vertices": vertices
                }
            ]
        
        else:
            # デフォルト：L字型
            return [
                {
                    "type": "poly",
                    "vertices": [(-size, -size), (size, -size), (size, 0), (-size, 0)]
                },
                {
                    "type": "poly",
                    "vertices": [(-size, 0), (0, 0), (0, size), (-size, size)]
                }
            ]
    
    def draw(self, screen):
        """非凸物体を描画"""
        # ボディの位置と回転を取得
        body_pos = self.body.position
        body_angle = self.body.angle
        
        # 各形状を描画
        for shape_def in self.shape_definitions:
            if shape_def["type"] == "poly":
                vertices = shape_def["vertices"]
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
                
                # 多角形を描画
                if len(world_vertices) >= 3:
                    pygame.draw.polygon(screen, self.color, world_vertices)
                    pygame.draw.polygon(screen, BLACK, world_vertices, 2)
            
            elif shape_def["type"] == "circle":
                offset = shape_def.get("offset", (0, 0))
                radius = shape_def["radius"]
                
                # オフセットを回転
                cos_a = math.cos(body_angle)
                sin_a = math.sin(body_angle)
                rotated_offset_x = offset[0] * cos_a - offset[1] * sin_a
                rotated_offset_y = offset[0] * sin_a + offset[1] * cos_a
                
                # ワールド座標を計算
                world_x = int(body_pos.x + rotated_offset_x)
                world_y = int(body_pos.y + rotated_offset_y)
                
                # 円を描画
                pygame.draw.circle(screen, self.color, (world_x, world_y), int(radius))
                pygame.draw.circle(screen, BLACK, (world_x, world_y), int(radius), 2)
    
    def remove(self):
        """物理空間から非凸物体を削除"""
        for shape in self.shapes:
            self.space.remove(shape)
        self.space.remove(self.body)


# 非凸物体の種類を定義
NON_CONVEX_SHAPES = {
    "L": {"color": RED, "mass": ANIMAL_MASS * 2},
    "T": {"color": PURPLE, "mass": ANIMAL_MASS * 2.5},
    "U": {"color": (255, 100, 100), "mass": ANIMAL_MASS * 2.2},
    "cross": {"color": (100, 255, 100), "mass": ANIMAL_MASS * 3},
    "star": {"color": (255, 215, 0), "mass": ANIMAL_MASS * 2.8},
}

