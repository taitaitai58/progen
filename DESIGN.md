# 動物タワーバトル 設計資料

## 1. ゲーム概要

### 1.1 ゲームの目的
ランダムに選ばれたメッシュオブジェクトを積み上げてタワーを作り、オブジェクトが土台から落ちないようにするゲーム。

### 1.2 ゲームの流れ
1. ランダムなメッシュが物理エンジンOFF状態で高所に表示される
2. プレイヤーが左右移動・回転で位置を調整
3. 決定ボタンで落下開始（物理エンジンON）
4. オブジェクトが土台から落ちたらゲームオーバー
5. 次のラウンドに進む（スコア加算）

## 2. ゲーム状態管理

### 2.1 ゲーム状態（GameState）
```
- MENU: メニュー画面
- PLAYING: ゲームプレイ中
- PLACING: オブジェクト配置中（物理エンジンOFF、位置調整中）
- FALLING: オブジェクト落下中（物理エンジンON）
- GAME_OVER: ゲームオーバー
- PAUSED: 一時停止
```

### 2.2 状態遷移図
```
MENU → PLAYING → PLACING → FALLING → (PLAYING or GAME_OVER)
                                    ↓
                              GAME_OVER
```

## 3. クラス設計

### 3.1 AnimalTowerBattle クラス（メインゲームクラス）

#### 属性
```python
class AnimalTowerBattle:
    # 基本設定
    screen: pygame.Surface
    clock: pygame.time.Clock
    space: pymunk.Space
    
    # ゲーム状態
    game_state: GameState
    score: int
    round: int
    
    # オブジェクト管理
    placed_objects: List[NonConvexObject]  # 配置済みオブジェクト
    current_object: Optional[NonConvexObject]  # 現在配置中のオブジェクト
    
    # メッシュ管理
    available_meshes: List[MeshData]  # 利用可能なメッシュリスト
    current_mesh_data: Optional[MeshData]  # 現在選択中のメッシュ
    
    # 土台（ゲームオーバー判定用）
    platform: pymunk.Body  # 土台の物理ボディ
    platform_y: float  # 土台のY座標
    
    # 配置パラメータ
    placement_height: float  # 配置開始時の高さ
    move_speed: float  # 左右移動速度
    rotate_speed: float  # 回転速度（度/フレーム）
    
    # ゲームオーバー判定
    game_over_threshold: float  # ゲームオーバー判定のY座標（土台より下）
```

#### 主要メソッド

##### 初期化・セットアップ
```python
def __init__(self)
    """ゲームを初期化"""
    
def load_available_meshes(self) -> List[MeshData]
    """meshes/フォルダから利用可能なメッシュを読み込む"""
    
def create_platform(self)
    """土台を作成（ゲームオーバー判定用）"""
```

##### ゲームループ
```python
def run(self)
    """メインゲームループ"""
    
def update(self, dt: float)
    """ゲーム状態を更新"""
    
def handle_events(self)
    """イベント処理"""
    
def render(self)
    """描画処理"""
```

##### オブジェクト管理
```python
def spawn_next_object(self)
    """次のオブジェクトを生成（物理エンジンOFF状態）"""
    
def select_random_mesh(self) -> MeshData
    """ランダムにメッシュを選択"""
    
def place_object(self)
    """現在のオブジェクトを配置（物理エンジンON）"""
    
def check_game_over(self) -> bool
    """ゲームオーバー条件をチェック"""
```

##### 操作処理
```python
def handle_placement_controls(self, keys)
    """配置中の操作（左右移動・回転）"""
    
def move_object_left(self)
    """オブジェクトを左に移動"""
    
def move_object_right(self)
    """オブジェクトを右に移動"""
    
def rotate_object_clockwise(self)
    """オブジェクトを時計回りに回転"""
    
def rotate_object_counterclockwise(self)
    """オブジェクトを反時計回りに回転"""
```

##### UI表示
```python
def draw_ui(self)
    """UI要素を描画（スコア、ラウンド、操作説明など）"""
    
def draw_game_over_screen(self)
    """ゲームオーバー画面を描画"""
```

### 3.2 MeshData クラス（データクラス）

```python
@dataclass
class MeshData:
    """メッシュデータを保持するクラス"""
    name: str  # メッシュ名（フォルダ名）
    folder_path: str  # メッシュフォルダのパス
    mesh_definitions: List[Dict]  # メッシュ定義（三角形リスト）
    texture_path: Optional[str]  # テクスチャ画像のパス
    mesh_center: Tuple[float, float]  # メッシュの重心
    image_size: Optional[Tuple[int, int]]  # 画像サイズ
```

## 4. 操作仕様

### 4.1 キーボード操作

#### 配置中（PLACING状態）
- **← / A**: オブジェクトを左に移動
- **→ / D**: オブジェクトを右に移動
- **Q**: オブジェクトを反時計回りに回転
- **E**: オブジェクトを時計回りに回転
- **Space / Enter**: オブジェクトを落下開始（物理エンジンON）
- **Esc**: ゲームを一時停止

#### ゲーム中（PLAYING状態）
- **R**: ゲームをリセット
- **Esc**: メニューに戻る

#### ゲームオーバー時
- **Space / Enter**: リトライ
- **Esc**: メニューに戻る

### 4.2 マウス操作（将来拡張用）
- マウスドラッグでオブジェクトの位置を調整（オプション）

## 5. ゲームロジック詳細

### 5.1 オブジェクト生成フロー

```
1. select_random_mesh() でランダムにメッシュを選択
2. spawn_next_object() でオブジェクトを生成
   - 位置: (SCREEN_WIDTH/2, placement_height)
   - 角度: 0度
   - 物理エンジン: OFF
3. ゲーム状態を PLACING に変更
```

### 5.2 配置フロー

```
1. プレイヤーが左右移動・回転で位置を調整
2. Space/Enterキーで place_object() を呼び出し
   - current_object.enable_physics() で物理エンジンをON
   - current_object を placed_objects に追加
   - current_object を None に設定
3. ゲーム状態を FALLING に変更
4. 一定時間後、またはオブジェクトが静止したら次のオブジェクト生成
```

### 5.3 ゲームオーバー判定

```python
def check_game_over(self) -> bool:
    """いずれかのオブジェクトが土台から落ちたかチェック"""
    for obj in self.placed_objects:
        x, y = obj.get_position()
        if y > self.game_over_threshold:
            return True
    return False
```

**判定条件:**
- 配置済みオブジェクトのY座標が `game_over_threshold` より大きい（下に落ちた）
- `game_over_threshold = platform_y + 100` （土台より100ピクセル下）

### 5.4 スコア計算

```
- 1オブジェクト配置: +10点
- ラウンド数 × 10点（ボーナス）
- 連続成功: 追加ボーナス（将来拡張）
```

## 6. 物理エンジン設定

### 6.1 物理パラメータ
```python
# config.py に追加
PLACEMENT_HEIGHT = 100  # 配置開始時の高さ（画面上部から）
MOVE_SPEED = 5.0  # 左右移動速度（ピクセル/フレーム）
ROTATE_SPEED = 5.0  # 回転速度（度/フレーム）
PLATFORM_Y = SCREEN_HEIGHT - 100  # 土台のY座標
GAME_OVER_THRESHOLD_OFFSET = 100  # 土台からのゲームオーバー判定オフセット
```

### 6.2 物理エンジンの状態管理
- **配置中**: `physics_enabled=False`（物理演算なし、手動で位置・角度を変更可能）
- **落下中**: `physics_enabled=True`（重力の影響を受ける）

## 7. メッシュ読み込み仕様

### 7.1 メッシュフォルダ構造
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

### 7.2 メッシュ読み込み処理
```python
def load_available_meshes(self) -> List[MeshData]:
    """meshes/フォルダ内のすべてのメッシュを読み込む"""
    1. meshes/フォルダ内のサブフォルダをスキャン
    2. 各フォルダ内のmesh.jsonを読み込み
    3. テクスチャ画像を検索（.png, .jpg, .jpeg, .bmp）
    4. MeshDataオブジェクトを作成してリストに追加
    5. メッシュが見つからない場合はエラーハンドリング
```

## 8. UI設計

### 8.1 表示要素

#### ゲーム中
- **左上**: スコア表示
- **右上**: ラウンド数表示
- **中央上部**: 操作説明（配置中のみ）
  - "← →: 移動  Q/E: 回転  Space: 落下"
- **画面下部**: 土台（視覚的な表示）

#### ゲームオーバー時
- **中央**: "GAME OVER" メッセージ
- **スコア表示**: 最終スコア
- **操作説明**: "Space: リトライ  Esc: メニュー"

### 8.2 視覚的フィードバック
- 配置中のオブジェクト: 半透明表示またはアウトライン表示
- 配置済みオブジェクト: 通常表示
- ゲームオーバー時: 画面を暗くする（オーバーレイ）

## 9. 実装の優先順位

### Phase 1: 基本機能
1. ✅ ゲームクラスの基本構造
2. ✅ メッシュ読み込み機能
3. ✅ オブジェクト生成・配置機能
4. ✅ 基本的な操作（移動・回転・落下）
5. ✅ ゲームオーバー判定

### Phase 2: UI・UX改善
1. UI表示（スコア、ラウンド、操作説明）
2. ゲームオーバー画面
3. 視覚的フィードバック改善

### Phase 3: 拡張機能
1. スコアシステムの詳細化
2. 難易度調整（落下速度、オブジェクト数など）
3. サウンドエフェクト
4. ハイスコア記録

## 10. 技術的な注意点

### 10.1 物理エンジンの状態管理
- 配置中は必ず物理エンジンをOFFにする
- 落下開始時に確実に物理エンジンをONにする
- オブジェクト削除時は物理エンジンをOFFにしてから削除

### 10.2 メッシュのスケーリング
- 既存のメッシュは0.2スケール（1/5）で読み込まれている
- 新しいメッシュも同様のスケーリングを適用

### 10.3 パフォーマンス
- 配置済みオブジェクトが多くなりすぎないように注意
- 画面外に落ちたオブジェクトは削除する（オプション）

### 10.4 エラーハンドリング
- メッシュファイルが見つからない場合
- テクスチャ画像が見つからない場合
- 物理エンジンの状態が不正な場合

## 11. ファイル構成

```
progen/
├── animal_tower_battle.py  # メインゲームクラス（新規作成）
├── animals.py              # NonConvexObjectクラス（既存）
├── config.py               # 設定（拡張）
├── mesh_editor.py          # メッシュエディター（既存）
├── start.py                # スタート画面（既存、拡張可能）
└── meshes/                 # メッシュデータ（既存）
```

## 12. 設定値の推奨値

```python
# config.py に追加する設定
PLACEMENT_HEIGHT = 150  # 配置開始時の高さ
MOVE_SPEED = 5.0  # 左右移動速度
ROTATE_SPEED = 5.0  # 回転速度（度/フレーム）
PLATFORM_Y = SCREEN_HEIGHT - 100  # 土台のY座標
GAME_OVER_THRESHOLD_OFFSET = 150  # ゲームオーバー判定オフセット
FALLING_WAIT_TIME = 2.0  # 落下後の待機時間（秒）
```
