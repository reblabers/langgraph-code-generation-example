from langgraph.graph import StateGraph, START, END
from nodes.node_1 import node_1
from nodes.node_2 import node_2
from nodes.node_3 import node_3
from decider import decide_mood
from state import State

def create_graph() -> StateGraph:
    # Build graph
    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)

    # Logic
    builder.add_edge(START, "node_1")
    builder.add_conditional_edges("node_1", decide_mood)
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)

    # Add
    graph = builder.compile()
    return graph 