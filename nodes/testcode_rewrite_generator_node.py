from utils.single_tool_caller import SingleToolCaller
from tools.apply_to_file import apply_to_file
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState, Fault
from typing_extensions import TypedDict
from textwrap import dedent
from typing import List
from utils.repository import Repository
from pathlib import Path
from utils.diff_applier import apply_diff_to_file
import difflib
import shutil


class LocalState(TypedDict):
    source_code: str
    test_code: str
    test_code_path: Path
    faults: List[Fault]
    diff: str

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code=global_state["source_code"],
            test_code=global_state["test_code"],
            test_code_path=global_state["test_code_path"],
            faults=global_state["faults"],
            diff=global_state["diff"],
        )


class TestRewriteGeneratorNode:

    def __init__(self, llm, repository: Repository):
        self.caller = SingleToolCaller(llm, apply_to_file)
        self.repository = repository
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
DIFFS:

{diffs}
            """).strip()),
            ("assistant", dedent("""
SUGGESTED TEST CODE DIFF:
```kotlin
{suggested_test_code_diff}
```
""").strip()),
            ("user", dedent("""
CURRENT TEST CLASS (failed):
```kotlin
{current_test_class}
```
            """).strip()),
            ("user", dedent("""
ERROR MESSAGE:
```
{error_message}
```
            """).strip()),
            ("user", dedent("""
INSTRUCTIONS: Your suggested test code is not compiling. \
Please rewrite the test code to fix the compilation error. \
Please output the diff snippet showing the changes relative to the current test code in Unified Diff format.
            """).strip()),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        result = await self._process(state)
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        # リポジトリをクリーン
        self.repository.clean()

        test_code_path = state["test_code_path"]
        faults = state["faults"]

        test_code = test_code_path.read_text()

        # テストコードの変更
        mutated_path = apply_diff_to_file(
            source_path=test_code_path,
            diff=state["diff"],
        )

        if mutated_path is None:
            print("Failed to apply diff to test code")
            return None
        
        shutil.copy(mutated_path, test_code_path)

        print("TEST APPLIED")

        # テストを実行. テストが失敗したら終了
        print("TESTING ON ORIGINAL")
        is_success, stdout, stderr = self.repository.test2()
        if is_success:
            print(f"OK TEST")
            return None

        print(f"NG TEST")

        mutated_test_code = test_code_path.read_text()

        new_diff = difflib.unified_diff(test_code.splitlines(), mutated_test_code.splitlines(), lineterm="")
        new_diff = "\n".join(new_diff)
        
        diffs = "\n---\n".join([f"REASON:\n{fault['reason']}\n\nDIFF:\n```\n{fault['diff']}\n```" for fault in state["faults"]])

        diff = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "original_class": state["source_code"],
                "diffs": diffs,
                "suggested_test_code_diff": new_diff,
                "current_test_class": mutated_test_code,
                "error_message": stderr,
            }
        )

        mutated_path = apply_diff_to_file(
            source_path=test_code_path,
            diff=diff,
        )

        if mutated_path is None:
            print("Failed to apply diff to test code")
            return None
        
        shutil.copy(mutated_path, test_code_path)

        mutated_test_code = test_code_path.read_text()

        new_diff = difflib.unified_diff(test_code.splitlines(), mutated_test_code.splitlines(), lineterm="")
        new_diff = "\n".join(new_diff)

        # デバッグ用にdiffを保存
        with open("debug/last_test_generator2.diff", "w") as f:
            f.write(new_diff)

        return {
            "diff": "new_diff",
        }
