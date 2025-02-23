from graph_builder2 import create_graph
from state import State
import os

def main():
    # 入力ファイルのパスを設定
    source_code_path = "kotlin/Finder.kt"
    test_code_path = "kotlin/FinderTest.kt"
    
    # 初期状態を設定
    inputs = {
        "source_code_path": source_code_path,
        "test_code_path": test_code_path,
        "graph_state": ""
    }
    
    # グラフを作成
    graph = create_graph()
    
    # グラフを実行
    result = graph.invoke(inputs)
    print(f"生成されたミューテーションファイル: {result['mutated_code_path']}")

if __name__ == "__main__":
    main() 