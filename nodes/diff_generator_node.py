from utils.single_tool_caller import SingleToolCaller
from tools.apply_to_file import apply_to_file
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState
from typing_extensions import TypedDict
from textwrap import dedent


class LocalState(TypedDict):
    source_file_name: str
    test_file_name: str
    source_code: str
    test_code: str

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_file_name=global_state["source_code_path"].name,
            test_file_name=global_state["test_code_path"].name,
            source_code=global_state["source_code"],
            test_code=global_state["test_code"],
        )


class DiffGeneratorNode:
    def __init__(self, llm):
        self.caller = SingleToolCaller(llm, apply_to_file)
        self.prompt_template = ChatPromptTemplate.from_messages([
            # TODO `CONTEXT:　{context_about_concern} `を追加
            #  that introduces a privacy violation similar to {diff}
            ("system", dedent("""
INSTRUCTION: Here is a Kotlin class and a test class with some unit tests for the class under test "CLASS_UNDER_TEST". "EXISTING_TEST_CLASS". \
Write a new version of the class under test in which each method is replaced by a new version of that method that contains a typical bug. \
Delimit the mutated part using the comment-pair `// MUTANT <START>` and `// MUTANT <END>` .

Finally, output the diff snippet showing the changes relative to the original code in Unified Diff format.
            """).strip()),
            ("user", dedent("""
CLASS_UNDER_TEST:
```kotlin
{class_under_test}
```
            """).strip()),
            ("user", dedent("""
EXISTING_TEST_CLASS:
```kotlin
{existing_test_class}
```
            """).strip()),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        result = await self._process(state)
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        diff = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "class_under_test": state["source_code"],
                "existing_test_class": state["test_code"],
                "source_file_name": state["source_file_name"],
                "test_file_name": state["test_file_name"],
            }
        )

        # デバッグ用にdiffを保存
        with open("debug/last_diff_generator.diff", "w") as f:
            f.write(diff)

        return {
            "diff": diff,
        }
