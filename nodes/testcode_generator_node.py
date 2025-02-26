from utils.single_tool_caller import SingleToolCaller
from tools.apply_to_file import apply_to_file
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState, Fault
from typing_extensions import TypedDict
from textwrap import dedent
from typing import List


class LocalState(TypedDict):
    source_code: str
    test_code: str
    faults: List[Fault]

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code=global_state["source_code"],
            test_code=global_state["test_code"],
            faults=global_state["faults"],
        )


class TestGeneratorNode:

    def __init__(self, llm):
        self.caller = SingleToolCaller(llm, apply_to_file)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", dedent("""
You are tasked with generating additional test cases for a Kotlin class. \
You will receive the original class:"ORIGINAL_CLASS", an existing test class:"EXISTING_TEST_CLASS", and a series of diffs:"DIFFS". \
Each diff represents a single fault that was introduced into the original class. \
Your goal is to write new test cases that will fail specifically because of the fault introduced in each diff, but would pass on the original, correct version of the class.

Write an extended version of the test class that contains extra test cases that will fail on the mutant version of the class, but would pass on the correct version. \
Finally, output the diff snippet showing the changes relative to the original code in Unified Diff format.
            """).strip()),
            ("user", dedent("""
ORIGINAL_CLASS:
```kotlin
{original_class}
```
            """).strip()),
            ("user", dedent("""
EXISTING_TEST_CLASS:
```kotlin
{existing_test_class}
```
            """).strip()),
            ("user", dedent("""
DIFFS:

{diffs}
            """).strip()),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        result = await self._process(state)
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        diffs = "\n---\n".join([f"REASON:\n{fault['reason']}\n\nDIFF:\n```\n{fault['diff']}\n```" for fault in state["faults"]])

        diff = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "original_class": state["source_code"],
                "existing_test_class": state["test_code"],
                "diffs": diffs,
            }
        )

        # デバッグ用にdiffを保存
        with open("debug/last_test_generator.diff", "w") as f:
            f.write(diff)

        return {
            "diff": "diff",
        }
