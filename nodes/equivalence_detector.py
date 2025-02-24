from utils.single_tool_caller import SingleToolCaller
from tools.output_equivalence import output_equivalence
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState
from typing_extensions import TypedDict
from textwrap import dedent
import json


class LocalState(TypedDict):
    source_code: str
    diff: str
    is_equivalent: bool

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code=global_state["source_code"],
            diff=global_state["diff"],
            is_equivalent=global_state["is_equivalent"],
        )


class EquivalenceDetectorNode:
    def __init__(self, llm):
        self.caller = SingleToolCaller(llm, output_equivalence)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", dedent("""
I'm going to show you a Kotlin class and a set of changes made to it. Here is the original Kotlin class: 'SOURCE_CODE'. Here is the set of changes applied to the class: 'DIFF'.

INSTRUCTION:
If applying these changes results in a class that behaves exactly the same as the original, Output 'True'. \
However, if the changes are not equivalent, Output 'False', and explain how execution of the original version can produce a different behavior compared to the modified version.
            """).strip()),
            ("user", dedent("""
SOURCE_CODE:
```kotlin
{source_code}
```
            """).strip()),
            ("user", dedent("""
DIFF:
```diff
{diff}
```
            """).strip()),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)

        result_json = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "source_code": state["source_code"],
                "diff": state["diff"],
            }
        )

        result = json.loads(result_json)

        return {
            **global_state,
            "is_equivalent": result["is_equivalent"],
            "reason_not_equivalent": result["reason"],
        }
