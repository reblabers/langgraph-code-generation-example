import asyncio
from credentials import get_default_credentials
from facade import get_bedrock_llm
from nodes.diff_generator_node import DiffGeneratorNode

async def main():
    # 認証情報とLLMの設定
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)
    
    # DiffGeneratorNodeのインスタンス化
    node = DiffGeneratorNode(llm)
    
    # GlobalStateの初期化
    global_state = {
        "source_code_path": "kotlin/Finder.kt",
        "test_code_path": "kotlin/FinderTest.kt"
    }
    
    try:
        # ノードの処理を実行
        state = await node.process(global_state)
        
        print("\n=== 生成されたDIFF ===")
        print(state["diff"])
        
        # DIFFをファイルに保存
        with open("temp.diff", "w") as f:
            f.write(state["diff"])
        print("\nDIFFを'temp.diff'に保存しました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 