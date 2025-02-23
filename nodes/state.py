from typing import TypedDict, Annotated, Optional
from dataclasses import dataclass
from typing_extensions import NotRequired
from pathlib import Path


class GlobalState(TypedDict):
    source_code_path: Optional[Path] = None
    test_code_path: Optional[Path] = None
    diff: Optional[str] = None
    mutated_code_path: Optional[Path] = None


def initial_state(source_code_path:Path, test_code_path:Path) -> GlobalState:
    return {
        "source_code_path": source_code_path,
        "test_code_path": test_code_path,
    }
