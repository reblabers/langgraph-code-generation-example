from nodes.state import GlobalState, initial_global_state_for_code, Fault
from langgraph.graph import StateGraph, START, END
from nodes.testcode_generator_node import TestGeneratorNode
from nodes.diff_test_applier_node import DiffTestApplierNode
from nodes.testcode_rewrite_generator_node import TestRewriteGeneratorNode
from utils.repository import Repository
from pathlib import Path
from typing import List


def build_test_generator_graph(llm, repository: Repository, is_debug: bool = True) -> StateGraph:
    test_generator = TestGeneratorNode(llm)
    diff_test_applier = DiffTestApplierNode(repository)
    testcode_rewrite_generator = TestRewriteGeneratorNode(llm, repository)
    builder = StateGraph(GlobalState)

    if is_debug:
        from nodes.diff_constant_node import DiffConstantNode
        diff_constant = DiffConstantNode()
        builder.add_node("test_generator", diff_constant.process)
    else:
        builder.add_node("test_generator", test_generator.process)

    builder.add_node("diff_test_applier", diff_test_applier.process)
    builder.add_node("testcode_rewrite_generator", testcode_rewrite_generator.process)

    if is_debug:
        builder.add_edge(START, "test_generator")
        builder.add_edge("test_generator", "diff_test_applier")
    else:
        builder.add_edge(START, "test_generator")
        builder.add_edge("test_generator", "testcode_rewrite_generator")
        builder.add_edge("testcode_rewrite_generator", "diff_test_applier")
    
    builder.add_edge("diff_test_applier", END)

    return builder.compile()


def initial_state(source_code_path: Path, test_code_path: Path, faults: List[Fault]) -> GlobalState:
    if not source_code_path.exists():
        raise FileNotFoundError(f"Source code file not found: {source_code_path}")
    if not test_code_path.exists():
        raise FileNotFoundError(f"Test code file not found: {test_code_path}")  
    return initial_global_state_for_code(source_code_path, test_code_path, faults)
