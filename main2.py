import asyncio
from nodes.equivalence_detector import EquivalenceDetectorNode
from utils.credentials import get_default_credentials
from utils.llm import get_bedrock_llm
from pathlib import Path


async def main():
    # 認証情報とLLMの設定
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)

    # EquivalenceDetectorNodeの初期化
    detector = EquivalenceDetectorNode(llm)

    # テスト用のグローバルステート
    global_state = {
        "source_code": """
class Calculator {
    fun add(a: Int, b: Int): Int {
        return a + b
    }
}
        """.strip(),
        "diff_faults": [
            # 等価な変更の例
            """
@@ -1,5 +1,5 @@
 class Calculator {
     fun add(a: Int, b: Int): Int {
-        return a + b
+        return b + a
     }
 }
            """.strip(),
            # 等価でない変更の例
            """
@@ -1,5 +1,5 @@
 class Calculator {
     fun add(a: Int, b: Int): Int {
-        return a + b
+        return a - b
     }
 }
            """.strip(),
        ]
    }

    # ノードの実行
    result = await detector.process(global_state)

    # 結果の表示
    print("Results:")
    for i, fault in enumerate(result["faults"], 1):
        print(f"\nDiff #{i}:")
        print(f"Is equivalent: {fault['is_equivalent']}")
        if fault["reason"]:
            print(f"Reason: {fault['reason']}")


if __name__ == "__main__":
    asyncio.run(main()) 