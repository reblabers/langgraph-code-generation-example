from typing import TypedDict, List, Optional
from typing import Annotated
from operator import add

class State(TypedDict, total=False):
    source_code_path: str
    test_code_path: str
    mutated_code_path: Optional[str]
    graph_state: str

    # Annotatedでstateを更新するreducerを指定する
    bar: Annotated[list[int], add] 