from utils.tool_caller import SingleToolCaller
from tools.output_diff import output_diff
from langchain_core.prompts import ChatPromptTemplate
from .state import GlobalState
from pathlib import Path
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
        self.tools = [output_diff]
        self.caller = SingleToolCaller(llm, self.tools)
        self.prompt_template = ChatPromptTemplate.from_messages([
            # TODO `CONTEXT:　{context_about_concern} `を追加
            ("system", dedent("""
INSTRUCTION: There is a Kotlin class `{source_file_name}` and a test class `{test_file_name}` that contains several unit tests for the class under test. Write a new version of `{source_file_name}` in which each method is replaced by a version that introduces a typical bug not detected by the current tests. Instead of outputting the entire modified code, provide only the diff snippet showing the changes relative to the original code in Unified Diff format.
""").strip()),
            ("user", "<class_under_test>{class_under_test}</class_under_test>"),
            ("user", "<existing_test_class>{existing_test_class}</existing_test_class>"),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        
        diff = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "class_under_test": state["source_code"],
                "existing_test_class": state["test_code"],
                "source_file_name": state["source_file_name"],
                "test_file_name": state["test_file_name"],
            }
        )

        return {
            **global_state,
            "diff": diff,
        }
