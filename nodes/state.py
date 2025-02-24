from typing import TypedDict, Annotated, Optional
from dataclasses import dataclass
from typing_extensions import NotRequired
from pathlib import Path


class GlobalState(TypedDict):
    source_code_path: Optional[Path] = None
    test_code_path: Optional[Path] = None
    source_code: Optional[str] = None
    test_code: Optional[str] = None
    diff: Optional[str] = None
    mutated_code_path: Optional[Path] = None
    mutated_code: Optional[str] = None
    is_equivalent: Optional[bool] = None
    reason_not_equivalent: Optional[str] = None


def initial_global_state(source_code_path: Path, test_code_path: Path) -> GlobalState:
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
