from nodes.state import GlobalState, initial_global_state
from langgraph.graph import StateGraph, START, END
from nodes.diff_generator_node import DiffGeneratorNode
from nodes.diff_applier_node import DiffApplierNode
from nodes.equivalence_detector import EquivalenceDetectorNode
from utils.repository import Repository
from pathlib import Path
from typing import Callable


def build_code_generator_graph(llm, repository: Repository, is_debug: bool = False) -> StateGraph:
    diff_generator = DiffGeneratorNode(llm)
    diff_applier = DiffApplierNode(repository)
    equivalence_detector = EquivalenceDetectorNode(llm)

    builder = StateGraph(GlobalState)

    if is_debug:
        from nodes.diff_constant_node import DiffConstantNode
        diff_constant = DiffConstantNode()
        builder.add_node("diff_generator", diff_constant.process)
    else:
        builder.add_node("diff_generator", diff_generator.process)

    builder.add_node("diff_applier", diff_applier.process)
    builder.add_node("equivalence_detector", equivalence_detector.process)

    builder.add_edge(START, "diff_generator")
    builder.add_edge("diff_generator", "diff_applier")
    builder.add_edge("diff_applier", "equivalence_detector")
    builder.add_edge("equivalence_detector", END)

    return builder.compile()


def initial_state(source_code_path: Path, test_code_path: Path) -> GlobalState:
    if not source_code_path.exists():
        raise FileNotFoundError(f"Source code file not found: {source_code_path}")
    if not test_code_path.exists():
        raise FileNotFoundError(f"Test code file not found: {test_code_path}")  
    return initial_global_state(source_code_path, test_code_path)
