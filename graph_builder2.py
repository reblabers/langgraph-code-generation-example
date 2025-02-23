from langgraph.graph import StateGraph, START, END
from nodes.node_1 import process as mutate_code
from state import State

def create_graph() -> StateGraph:
    # グラフを構築
    builder = StateGraph(State)
    
    # ノードを追加
    builder.add_node("mutate_code", mutate_code)
    
    # エッジを追加
    builder.add_edge(START, "mutate_code")
    builder.add_edge("mutate_code", END)
    
    # グラフをコンパイル
    graph = builder.compile()
    return graph 