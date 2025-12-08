# APIリファレンス & 実装ガイド

## 目次
1. [NonConvexObject API](#nonconvexobject-api)
2. [pymunk Space API](#pymunk-space-api)
3. [メッシュ読み込み API](#メッシュ読み込み-api)
4. [pygame API（主要なもの）](#pygame-api主要なもの)
5. [実装のヒント](#実装のヒント)

---

## NonConvexObject API

### クラス概要
非凸形状（三角形メッシュ）の物理オブジェクトを管理するクラス。物理エンジンのON/OFF、位置・角度の変更、描画などの機能を提供します。

---

### オブジェクト生成

#### `NonConvexObject.create(space, x, y, mesh_definitions, ...)`
**クラスメソッド** - オブジェクトを生成する便利メソッド

```python
obj = NonConvexObject.create(
    space=pymunk.Space(),           # 物理空間（必須）
    x=100,                          # 初期X座標（必須）
    y=100,                          # 初期Y座標（必須）
    mesh_definitions=[...],         # メッシュ定義リスト（必須）
    color=(255, 100, 100),          # 色（デフォルト: (255, 100, 100)）
    mass=None,                      # 質量（Noneの場合はANIMAL_MASS * 2）
    texture_path="texture.png",     # テクスチャ画像のパス
    mesh_center=(0, 0),             # メッシュの重心位置
    image_size=(width, height),     # 画像サイズ
    physics_enabled=True             # 物理エンジンの初期状態（デフォルト: True）
)
```

**戻り値**: `NonConvexObject` インスタンス

**使用例**:
```python
obj = NonConvexObject.create(
    space=self.space,
    x=SCREEN_WIDTH // 2,
    y=150,
    mesh_definitions=mesh_defs,
    texture_path="meshes/mesh1/texture.png",
    physics_enabled=False  # 配置中はOFF
)
```

---

#### `__init__(space, x, y, color, mesh_definitions, ...)`
**コンストラクタ** - 直接インスタンス化も可能（通常は`create()`を使用）

---

### 物理エンジン制御

#### `enable_physics()`
物理エンジンを有効にする（物理空間に追加）

```python
obj.enable_physics()
```

**動作**:
- BodyとShapeを物理空間（Space）に追加
- 重力の影響を受けるようになる
- 他のオブジェクトと衝突判定が有効になる

**使用例**:
```python
# 配置が完了したら物理エンジンをON
if event.key == pygame.K_SPACE:
    obj.enable_physics()
```

---

#### `disable_physics()`
物理エンジンを無効にする（描画は継続）

```python
obj.disable_physics()
```

**動作**:
- BodyとShapeを物理空間から削除
- 重力の影響を受けなくなる
- 衝突判定が無効になる
- 描画は継続される（位置・角度は手動で変更可能）

**使用例**:
```python
# 配置中は物理エンジンをOFF
obj = NonConvexObject.create(..., physics_enabled=False)
# または後からOFFにする
obj.disable_physics()
```

---

#### `is_physics_enabled() -> bool`
物理エンジンが有効かどうかを返す

```python
if obj.is_physics_enabled():
    print("物理エンジンはONです")
else:
    print("物理エンジンはOFFです")
```

**戻り値**: `True`（有効）または `False`（無効）

---

### 位置・角度の操作

#### `set_position(x, y)`
オブジェクトの位置を設定

```python
obj.set_position(200, 300)
```

**パラメータ**:
- `x`: X座標（ピクセル）
- `y`: Y座標（ピクセル）

**注意**: 物理エンジンがOFFの時のみ有効に動作（ONの時は物理演算で上書きされる可能性がある）

---

#### `get_position() -> (x, y)`
オブジェクトの位置を取得

```python
x, y = obj.get_position()
```

**戻り値**: `(x, y)` タプル

**使用例**:
```python
# ゲームオーバー判定
x, y = obj.get_position()
if y > GAME_OVER_THRESHOLD:
    game_over = True
```

---

#### `set_angle(angle)`
オブジェクトの角度を設定（ラジアン）

```python
obj.set_angle(math.pi / 4)  # 45度
```

**パラメータ**:
- `angle`: 角度（ラジアン）

---

#### `set_angle_degrees(angle_degrees)`
オブジェクトの角度を設定（度）

```python
obj.set_angle_degrees(45)  # 45度
```

**パラメータ**:
- `angle_degrees`: 角度（度）

**使用例**:
```python
# 回転操作
if keys[pygame.K_q]:
    current_angle = obj.get_angle_degrees()
    obj.set_angle_degrees(current_angle - 5)  # 反時計回り
```

---

#### `get_angle() -> float`
オブジェクトの角度を取得（ラジアン）

```python
angle = obj.get_angle()
```

**戻り値**: 角度（ラジアン）

---

#### `get_angle_degrees() -> float`
オブジェクトの角度を取得（度）

```python
angle = obj.get_angle_degrees()
```

**戻り値**: 角度（度）

---

### 速度・角速度の操作

#### `set_velocity(vx, vy)`
オブジェクトの速度を設定

```python
obj.set_velocity(0, 100)  # 下向きに100ピクセル/秒
```

**パラメータ**:
- `vx`: X方向の速度
- `vy`: Y方向の速度

**注意**: 物理エンジンがONの時のみ有効

---

#### `get_velocity() -> (vx, vy)`
オブジェクトの速度を取得

```python
vx, vy = obj.get_velocity()
```

**戻り値**: `(vx, vy)` タプル（物理エンジンOFF時は`(0, 0)`）

---

#### `set_angular_velocity(angular_velocity)`
オブジェクトの角速度を設定

```python
obj.set_angular_velocity(1.0)  # 1ラジアン/秒
```

**パラメータ**:
- `angular_velocity`: 角速度（ラジアン/秒）

---

#### `get_angular_velocity() -> float`
オブジェクトの角速度を取得

```python
angular_vel = obj.get_angular_velocity()
```

**戻り値**: 角速度（ラジアン/秒、物理エンジンOFF時は`0`）

---

### 描画・削除

#### `draw(screen)`
オブジェクトを描画

```python
obj.draw(self.screen)
```

**パラメータ**:
- `screen`: pygame.Surface オブジェクト

**動作**:
- テクスチャ画像がある場合は画像を描画
- テクスチャがない場合は三角形メッシュを描画
- 位置と回転を考慮して描画

**使用例**:
```python
# ゲームループ内で描画
for obj in self.placed_objects:
    obj.draw(self.screen)
if self.current_object:
    self.current_object.draw(self.screen)
```

---

#### `remove()`
物理空間からオブジェクトを削除

```python
obj.remove()
```

**動作**:
- 物理エンジンをOFFにしてから削除
- 物理空間から完全に削除される

**注意**: 描画リストからも削除する必要がある

---

### 内部プロパティ（直接アクセス可能）

#### `self.body`
pymunkのBodyオブジェクト（直接アクセス可能）

```python
# 直接アクセス例（通常は推奨されない）
obj.body.position = (100, 200)
obj.body.angle = math.pi / 4
```

---

#### `self.shapes`
pymunkのShapeオブジェクトのリスト

```python
# 各シェイプのプロパティにアクセス可能
for shape in obj.shapes:
    shape.friction = 0.5
    shape.elasticity = 0.3
```

---

#### `self.space`
pymunkの物理空間への参照

---

#### `self.mass`
オブジェクトの質量

---

#### `self.color`
オブジェクトの色（テクスチャがない場合に使用）

---

#### `self.texture_path`
テクスチャ画像のパス

---

## pymunk Space API

### Space の作成と設定

#### `pymunk.Space()`
物理空間を作成

```python
space = pymunk.Space()
space.gravity = (0, 981)  # 重力設定（下向き）
```

**使用例**:
```python
self.space = pymunk.Space()
self.space.gravity = GRAVITY  # config.pyから取得
```

---

#### `space.step(dt)`
物理演算を1ステップ進める

```python
space.step(1.0 / FPS)  # 1フレーム分の物理演算
```

**パラメータ**:
- `dt`: 経過時間（秒）

**使用例**:
```python
# ゲームループ内で呼び出す
dt = self.clock.tick(FPS) / 1000.0
self.space.step(dt)
```

---

### 静的オブジェクト（土台・壁など）の作成

#### `pymunk.Body(body_type=pymunk.Body.STATIC)`
静的ボディを作成（動かないオブジェクト）

```python
ground_body = pymunk.Body(body_type=pymunk.Body.STATIC)
```

---

#### `pymunk.Segment(body, start, end, radius)`
線分シェイプを作成（地面・壁など）

```python
ground_shape = pymunk.Segment(
    ground_body,
    (0, GROUND_Y),           # 開始点
    (SCREEN_WIDTH, GROUND_Y), # 終了点
    5                         # 太さ（半径）
)
ground_shape.friction = 1.0
space.add(ground_body, ground_shape)
```

**使用例**:
```python
def create_platform(self):
    """土台を作成"""
    platform_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    platform_shape = pymunk.Segment(
        platform_body,
        (0, PLATFORM_Y),
        (SCREEN_WIDTH, PLATFORM_Y),
        10
    )
    platform_shape.friction = 1.0
    self.space.add(platform_body, platform_shape)
    self.platform_y = PLATFORM_Y
```

---

## メッシュ読み込み API

### メッシュフォルダ構造
```
meshes/
├── mesh1/
│   ├── mesh.json
│   └── texture.png
├── mesh2/
│   ├── mesh.json
│   └── texture.png
└── ...
```

### メッシュデータの読み込み

#### `json.load()` と `TriangleMesh.from_dict()`
メッシュJSONファイルを読み込む

```python
import json
import os
from mesh_editor import TriangleMesh

def load_mesh(mesh_folder):
    """メッシュを読み込む"""
    mesh_json = os.path.join(mesh_folder, "mesh.json")
    
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
    
    # テクスチャが見つからない場合、フォルダ内を検索
    if not image_path or not os.path.exists(image_path):
        for ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            for file in os.listdir(mesh_folder):
                if file.lower().endswith(ext):
                    image_path = os.path.join(mesh_folder, file)
                    break
            if image_path and os.path.exists(image_path):
                break
    
    # メッシュ定義を変換（0.2スケール）
    mesh_definitions = []
    scale = 0.2
    for mesh in meshes:
        triangles = mesh.triangles
        for triangle in triangles:
            scaled_triangle = [(vx * scale, vy * scale) for vx, vy in triangle]
            mesh_definitions.append({
                "type": "poly",
                "vertices": scaled_triangle
            })
    
    return {
        "mesh_definitions": mesh_definitions,
        "texture_path": image_path if image_path and os.path.exists(image_path) else None,
        "mesh_center": (meshes[0].x if meshes else 0, meshes[0].y if meshes else 0),
        "image_size": None  # 必要に応じて設定
    }
```

---

### 利用可能なメッシュをスキャン

#### `os.listdir()` と `os.path.isdir()`
メッシュフォルダをスキャン

```python
import os

def load_available_meshes():
    """利用可能なメッシュをすべて読み込む"""
    meshes_dir = "meshes"
    available_meshes = []
    
    if not os.path.exists(meshes_dir):
        return available_meshes
    
    for item in os.listdir(meshes_dir):
        mesh_folder = os.path.join(meshes_dir, item)
        if os.path.isdir(mesh_folder):
            mesh_json = os.path.join(mesh_folder, "mesh.json")
            if os.path.exists(mesh_json):
                mesh_data = load_mesh(mesh_folder)
                available_meshes.append({
                    "name": item,
                    "folder_path": mesh_folder,
                    **mesh_data
                })
    
    return available_meshes
```

---

## pygame API（主要なもの）

### 初期化

#### `pygame.init()`
pygameを初期化

```python
pygame.init()
```

---

#### `pygame.display.set_mode((width, height))`
画面を作成

```python
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
```

---

#### `pygame.time.Clock()`
フレームレート制御用のクロックを作成

```python
clock = pygame.time.Clock()
clock.tick(FPS)  # FPSを制限
```

---

### イベント処理

#### `pygame.event.get()`
イベントを取得

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            # スペースキーが押された
            pass
```

---

#### `pygame.key.get_pressed()`
現在押されているキーを取得

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_LEFT]:
    # 左矢印キーが押されている
    pass
```

---

### 描画

#### `screen.fill(color)`
画面を塗りつぶす

```python
screen.fill(BLACK)
```

---

#### `pygame.font.SysFont(name, size)`
フォントを作成

```python
font = pygame.font.SysFont(None, 36)
text = font.render("Score: 100", True, WHITE)
screen.blit(text, (10, 10))
```

---

#### `screen.blit(surface, position)`
画像やテキストを描画

```python
screen.blit(text_surface, (x, y))
```

---

## 実装のヒント

### 1. ランダムなメッシュを選んで高所に表示（物理エンジンOFF）

**必要なAPI**:
- `load_available_meshes()` - メッシュリストを取得
- `random.choice()` - ランダム選択
- `NonConvexObject.create()` - オブジェクト生成（`physics_enabled=False`）

**実装例**:
```python
import random

def spawn_next_object(self):
    """次のオブジェクトを生成"""
    # ランダムにメッシュを選択
    mesh_data = random.choice(self.available_meshes)
    
    # 高所に配置（物理エンジンOFF）
    self.current_object = NonConvexObject.create(
        space=self.space,
        x=SCREEN_WIDTH // 2,
        y=PLACEMENT_HEIGHT,
        mesh_definitions=mesh_data["mesh_definitions"],
        color=(255, 100, 100),
        texture_path=mesh_data["texture_path"],
        mesh_center=mesh_data["mesh_center"],
        image_size=mesh_data["image_size"],
        physics_enabled=False  # 重要：OFF状態で生成
    )
    
    self.game_state = GameState.PLACING
```

---

### 2. 左右移動と回転で位置を決定

**必要なAPI**:
- `pygame.key.get_pressed()` - キー入力取得
- `get_position()` / `set_position()` - 位置の取得・設定
- `get_angle_degrees()` / `set_angle_degrees()` - 角度の取得・設定

**実装例**:
```python
def handle_placement_controls(self):
    """配置中の操作を処理"""
    if not self.current_object:
        return
    
    keys = pygame.key.get_pressed()
    
    # 左右移動
    x, y = self.current_object.get_position()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        x -= MOVE_SPEED
        self.current_object.set_position(x, y)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x += MOVE_SPEED
        self.current_object.set_position(x, y)
    
    # 回転
    if keys[pygame.K_q]:
        angle = self.current_object.get_angle_degrees()
        self.current_object.set_angle_degrees(angle - ROTATE_SPEED)
    elif keys[pygame.K_e]:
        angle = self.current_object.get_angle_degrees()
        self.current_object.set_angle_degrees(angle + ROTATE_SPEED)
```

---

### 3. ボタンで落下開始（物理エンジンON）

**必要なAPI**:
- `pygame.event.get()` - イベント取得
- `enable_physics()` - 物理エンジンをON

**実装例**:
```python
def handle_events(self):
    """イベント処理"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if self.game_state == GameState.PLACING:
                    # 落下開始
                    self.place_object()
    
    return True

def place_object(self):
    """オブジェクトを配置（物理エンジンON）"""
    if self.current_object:
        self.current_object.enable_physics()  # 物理エンジンをON
        self.placed_objects.append(self.current_object)
        self.current_object = None
        self.game_state = GameState.FALLING
```

---

### 4. ゲームオーバー判定（オブジェクトが土台から落ちたか）

**必要なAPI**:
- `get_position()` - 各オブジェクトの位置を取得
- 位置のY座標と土台のY座標を比較

**実装例**:
```python
def check_game_over(self) -> bool:
    """ゲームオーバー条件をチェック"""
    game_over_threshold = self.platform_y + GAME_OVER_THRESHOLD_OFFSET
    
    for obj in self.placed_objects:
        x, y = obj.get_position()
        if y > game_over_threshold:
            return True
    
    return False

# ゲームループ内でチェック
def update(self, dt):
    """ゲーム状態を更新"""
    if self.game_state == GameState.FALLING:
        # 物理演算を進める
        self.space.step(dt)
        
        # ゲームオーバー判定
        if self.check_game_over():
            self.game_state = GameState.GAME_OVER
        else:
            # 一定時間後、次のオブジェクトを生成
            # （オプション：オブジェクトが静止したかチェック）
            self.spawn_next_object()
```

---

### 5. メッシュの読み込みと管理

**必要なAPI**:
- `os.listdir()` / `os.path.isdir()` - フォルダスキャン
- `json.load()` - JSON読み込み
- `TriangleMesh.from_dict()` - メッシュデータ変換

**実装例**:
```python
def load_available_meshes(self):
    """利用可能なメッシュを読み込む"""
    meshes_dir = "meshes"
    self.available_meshes = []
    
    if not os.path.exists(meshes_dir):
        print("メッシュフォルダが見つかりません")
        return
    
    for item in os.listdir(meshes_dir):
        mesh_folder = os.path.join(meshes_dir, item)
        if os.path.isdir(mesh_folder):
            try:
                mesh_data = self.load_mesh_data(mesh_folder)
                self.available_meshes.append({
                    "name": item,
                    "folder_path": mesh_folder,
                    **mesh_data
                })
            except Exception as e:
                print(f"メッシュ {item} の読み込みに失敗: {e}")
    
    if not self.available_meshes:
        print("利用可能なメッシュがありません")
```

---

### 6. ゲームループの基本構造

**必要なAPI**:
- `pygame.time.Clock()` - フレームレート制御
- `space.step()` - 物理演算
- `draw()` - 描画

**実装例**:
```python
def run(self):
    """メインゲームループ"""
    running = True
    
    while running:
        # イベント処理
        running = self.handle_events()
        
        # ゲーム状態の更新
        dt = self.clock.tick(FPS) / 1000.0
        self.update(dt)
        
        # 描画
        self.render()
        
        pygame.display.flip()
    
    pygame.quit()

def update(self, dt):
    """ゲーム状態を更新"""
    if self.game_state == GameState.PLACING:
        # 配置中の操作を処理
        self.handle_placement_controls()
    
    elif self.game_state == GameState.FALLING:
        # 物理演算を進める
        self.space.step(dt)
        
        # ゲームオーバー判定
        if self.check_game_over():
            self.game_state = GameState.GAME_OVER

def render(self):
    """描画処理"""
    self.screen.fill(BLACK)
    
    # 土台を描画（オプション）
    pygame.draw.rect(self.screen, GREEN, 
                    (0, self.platform_y, SCREEN_WIDTH, 10))
    
    # 配置済みオブジェクトを描画
    for obj in self.placed_objects:
        obj.draw(self.screen)
    
    # 現在配置中のオブジェクトを描画
    if self.current_object:
        self.current_object.draw(self.screen)
    
    # UIを描画
    self.draw_ui()
    
    if self.game_state == GameState.GAME_OVER:
        self.draw_game_over_screen()
```

---

### 7. 状態管理の実装

**必要なAPI**:
- Enum（状態管理用）

**実装例**:
```python
from enum import Enum

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PLACING = "placing"
    FALLING = "falling"
    GAME_OVER = "game_over"
    PAUSED = "paused"

# 使用例
self.game_state = GameState.PLACING

if self.game_state == GameState.PLACING:
    # 配置中の処理
    pass
```

---

## 実装のチェックリスト

### Phase 1: 基本機能
- [ ] `AnimalTowerBattle`クラスの基本構造
- [ ] 物理空間（`pymunk.Space`）の作成
- [ ] 土台の作成（静的オブジェクト）
- [ ] メッシュ読み込み機能
- [ ] ランダムメッシュ選択
- [ ] オブジェクト生成（物理エンジンOFF）
- [ ] 左右移動・回転操作
- [ ] 落下開始（物理エンジンON）
- [ ] ゲームオーバー判定
- [ ] 基本的な描画

### Phase 2: UI・UX
- [ ] スコア表示
- [ ] ラウンド数表示
- [ ] 操作説明の表示
- [ ] ゲームオーバー画面
- [ ] 視覚的フィードバック

### Phase 3: 拡張
- [ ] スコア計算ロジック
- [ ] 難易度調整
- [ ] サウンドエフェクト
- [ ] ハイスコア記録

---

## よくある質問（FAQ）

### Q: 物理エンジンがOFFの時、位置を変更しても反映されない？
A: `disable_physics()`を呼び出した後、`set_position()`で位置を変更すれば反映されます。物理エンジンがOFFの時は手動で位置・角度を変更可能です。

### Q: メッシュが見つからない場合はどうする？
A: エラーハンドリングを追加し、フォールバックメッシュを生成するか、エラーメッセージを表示してください。

### Q: オブジェクトが画面外に落ちた場合の処理は？
A: `get_position()`で位置を確認し、画面外に出たオブジェクトは`remove()`で削除することを推奨します。

### Q: 物理演算のパフォーマンスが悪い場合は？
A: `space.step()`の呼び出し頻度を調整するか、オブジェクト数に上限を設けることを検討してください。

---

## 参考リンク

- [pymunk公式ドキュメント](https://www.pymunk.org/)
- [pygame公式ドキュメント](https://www.pygame.org/docs/)
- 既存コード: `test_game.py` - 実装例として参考にできます
