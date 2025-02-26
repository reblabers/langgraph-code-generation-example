from typing import TypedDict, Optional, List
from pathlib import Path


class Fault(TypedDict):
    diff: str
    is_equivalent: bool
    reason: Optional[str] = None


class GlobalState(TypedDict):
    source_code_path: Optional[Path] = None
    test_code_path: Optional[Path] = None
    source_code: Optional[str] = None
    test_code: Optional[str] = None
    
    diff: Optional[str] = None
    diff_faults: Optional[List[str]] = None
    faults: Optional[List[Fault]] = None


def initial_global_state_for_faults(source_code_path: Path, test_code_path: Path) -> GlobalState:
    with open(source_code_path) as f:
        source_code = f.read()
    
    with open(test_code_path) as f:
        test_code = f.read()

    return {
        "source_code_path": source_code_path,
        "test_code_path": test_code_path,
        "source_code": source_code,
        "test_code": test_code,
    }


def initial_global_state_for_code(source_code_path: Path, test_code_path: Path, faults: List[Fault]) -> GlobalState:
    with open(source_code_path) as f:
        source_code = f.read()
    
    with open(test_code_path) as f:
        test_code = f.read()

    return {
        "source_code_path": source_code_path,
        "test_code_path": test_code_path,
        "source_code": source_code,
        "test_code": test_code,
        "faults": faults,
    }
