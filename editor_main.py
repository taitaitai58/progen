"""
メッシュエディターのメインエントリーポイント

使い方:
    python editor_main.py <画像パス> [スケール]

例:
    python editor_main.py meshes/mesh1/texsture.png 0.1
    python editor_main.py meshes/mesh1/texsture.png 0.2
"""
from mesh_editor import MeshEditor
import sys


def main():
    """エディターを開始"""
    # コマンドライン引数を解析
    image_path = None
    scale = None
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            scale = float(sys.argv[2])
            if scale <= 0 or scale > 1:
                print("警告: スケールは0.0〜1.0の範囲で指定してください")
                scale = None
        except ValueError:
            print(f"警告: 無効なスケール値 '{sys.argv[2]}' - デフォルト値を使用します")
    
    # エディターを作成
    editor = MeshEditor(scale=scale)
    
    if image_path:
        editor.load_background_image(image_path)
        print(f"画像を読み込みました: {image_path}")
        print(f"スケール: {editor.scale}")
    
    editor.run()


if __name__ == "__main__":
    main()
