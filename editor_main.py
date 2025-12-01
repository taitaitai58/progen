"""
メッシュエディターのメインエントリーポイント
"""
from mesh_editor import MeshEditor
import sys


def main():
    """エディターを開始"""
    editor = MeshEditor()
    
    # コマンドライン引数から画像パスを取得
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        editor.load_background_image(image_path)
    
    editor.run()


if __name__ == "__main__":
    main()


