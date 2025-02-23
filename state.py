from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    graph_state: str

    # Annotatedでstateを更新するreducerを指定する
    bar: Annotated[list[int], add] 