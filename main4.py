from nodes.diff_applier_node import DiffApplierNode
from pathlib import Path

def main():
    # DiffApplierNodeのインスタンス化
    node = DiffApplierNode()
    
    # GlobalStateの初期化
    global_state = {
        "source_code_path": Path("kotlin/Finder.kt"),
        "diff": Path("temp.diff").read_text()
    }
    
    try:
        # ノードの処理を実行
        state = node.process(global_state)
        
        print("\n=== DIFFの適用が完了しました ===")
        print(f"変更されたファイル: {state['mutated_code_path']}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
