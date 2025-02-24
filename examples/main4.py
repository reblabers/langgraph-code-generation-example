from nodes.diff_applier_node import DiffApplierNode
from pathlib import Path
from utils.repository import Repository
from nodes.state import GlobalState, initial_state
from langgraph.graph import StateGraph, START, END
from nodes.equivalence_detector import EquivalenceDetectorNode
import asyncio
from utils.credentials import get_default_credentials
from utils.llm import get_bedrock_llm


async def main():
    credentials = get_default_credentials()
    llm = get_bedrock_llm(credentials)

    repository = Repository(Path("repositories/kotlin-tracer-mcp"))

    diff_applier = DiffApplierNode(repository)
    equivalence_detector = EquivalenceDetectorNode(llm)

    # GlobalStateの初期化
    global_state = initial_state(
        source_code_path=Path("repositories/kotlin-tracer-mcp/src/main/kotlin/com/example/Finder.kt"),
        test_code_path=Path("repositories/kotlin-tracer-mcp/src/test/kotlin/com/example/FinderTest.kt"),
    )
    global_state = {
        **global_state,
        "diff": Path("kotlin/temp.diff").read_text()
    }

    # グラフを構築
    builder = StateGraph(GlobalState)
    
    # ノードを追加
    builder.add_node("diff_applier", diff_applier.process)
    builder.add_node("equivalence_detector", equivalence_detector.process)

    # エッジを追加
    builder.add_edge(START, "diff_applier")
    builder.add_edge("diff_applier", "equivalence_detector")
    builder.add_edge("equivalence_detector", END)
    
    # グラフをコンパイル
    graph = builder.compile()
    
    # グラフを実行
    state = await graph.ainvoke(global_state)
    # print(state)


if __name__ == "__main__":
    asyncio.run(main())
