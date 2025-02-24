from nodes.state import GlobalState, initial_global_state
from langgraph.graph import StateGraph, START, END
from nodes.diff_generator_node import DiffGeneratorNode
from nodes.diff_applier_node import DiffApplierNode
from nodes.equivalence_detector import EquivalenceDetectorNode
from utils.repository import Repository
from pathlib import Path
from typing import Callable


def build_code_generator_graph(llm, repository: Repository) -> StateGraph:
    diff_generator = DiffGeneratorNode(llm)
    diff_applier = DiffApplierNode(repository)
    equivalence_detector = EquivalenceDetectorNode(llm)

    from nodes.diff_constant_node import DiffConstantNode
    diff_constant = DiffConstantNode()

    builder = StateGraph(GlobalState)

    # builder.add_node("diff_generator", diff_generator.process)
    builder.add_node("diff_generator", diff_constant.process)
    builder.add_node("diff_applier", diff_applier.process)
    builder.add_node("equivalence_detector", equivalence_detector.process)

    builder.add_edge(START, "diff_generator")
    builder.add_edge("diff_generator", "diff_applier")
    builder.add_edge("diff_applier", END)
    # builder.add_edge("diff_applier", "equivalence_detector")
    # builder.add_edge("equivalence_detector", END)

    return builder.compile()


def initial_state(source_code_path: Path, test_code_path: Path) -> GlobalState:
    return initial_global_state(source_code_path, test_code_path)
