from utils.diff_applier import apply_diff_to_file
from nodes.state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict


class LocalState(TypedDict):
    diff: str
    source_code_path: Path

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            diff=global_state["diff"],
            source_code_path=global_state["source_code_path"],
        )


class DiffApplierNode:
    def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)

        mutated_path = apply_diff_to_file(
            source_path=state["source_code_path"],
            diff=state["diff"],
        )
        
        return {
            **global_state,
            "mutated_code_path": mutated_path,
        } 
