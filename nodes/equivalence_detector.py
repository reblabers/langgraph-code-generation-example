from utils.single_tool_caller import SingleToolCaller
from tools.output_equivalence import output_equivalence
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState
from typing_extensions import TypedDict
from textwrap import dedent
import json
from typing import List


class LocalState(TypedDict):
    source_code: str
    diff_faults: List[str]

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code=global_state["source_code"],
            diff_faults=global_state["diff_faults"],
        )


class EquivalenceDetectorNode:
    def __init__(self, llm):
        self.caller = SingleToolCaller(llm, output_equivalence)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", dedent("""
I'm going to show you a Kotlin class and a set of changes made to it. Here is the original Kotlin class: 'SOURCE_CODE'. \
Below, I will show you multiple changes (DIFFs) applied to this class, each with an index number.

INSTRUCTION:
For each DIFF, determine if applying these changes results in a class that behaves exactly the same as the original.
For each DIFF, output:
- 'True' if the changes are equivalent
- 'False' if the changes are not equivalent, and explain how execution of the original version can produce a different behavior compared to the modified version.
            """).strip()),
            ("user", dedent("""
SOURCE_CODE:
```kotlin
{source_code}
```
            """).strip()),
            ("user", dedent("""
{diffs_with_index}
            """).strip()),
        ])

    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        result = await self._process(state)
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        source_code = state["source_code"]
        diff_faults = state["diff_faults"]

        if not diff_faults:
            return {
                "faults": [],
            }

        # Format diffs with index numbers
        diffs_with_index = "\n\n".join([
            f"DIFF #{i}:\n```diff\n{diff}\n```"
            for i, diff in enumerate(diff_faults, 1)
        ])

        result_json = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "source_code": source_code,
                "diffs_with_index": diffs_with_index,
            }
        )
        result = json.loads(result_json)

        faults = []
        for i, diff in enumerate(diff_faults):
            fault_result = result["results"][i]
            faults.append({
                "diff": diff,
                "is_equivalent": fault_result["is_equivalent"],
                "reason": fault_result["reason"],
            })

        return {
            "faults": faults,
        }
