from utils.tool_caller import SingleToolCaller
from tools.apply_diff import apply_diff
from langchain_core.prompts import ChatPromptTemplate
from nodes.state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict


class LocalState(TypedDict):
    source_code_path: Path
    test_code_path: Path

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code_path=global_state["source_code_path"],
            test_code_path=global_state["test_code_path"],
        )


class DiffGeneratorNode:
    def __init__(self, llm):
        self.tools = [apply_diff]
        self.caller = SingleToolCaller(llm, self.tools)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "テスト対象のクラス '''{source_file_name}'' のKotlinクラスといくつかのユニットテストを含むテストクラス '''{test_file_name}'' があります。"
            + "各メソッドが、動作不良を引き起こす典型的なバグを含む、そのメソッドの新しいバージョンで置き換えられた class_under_test の新しいバージョンを書きます。"
            + "変異させるコードをUnified形式のDIFFファイルで出力してください。"),
            ("user", "<class_under_test>{class_under_test}</class_under_test>"),
            ("user", "<existing_test_class>{existing_test_class}</existing_test_class>"),
        ])
    
    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        
        # ソースコードとテストコードを読み込み
        with open(state["source_code_path"]) as f:
            source_code = f.read()
        with open(state["test_code_path"]) as f:
            test_code = f.read()

        # ToolCallerでDIFFを生成
        diff = await self.caller.call(
            prompt_template=self.prompt_template,
            invoke_args={
                "class_under_test": source_code,
                "existing_test_class": test_code,
                "source_file_name": state["source_code_path"].name,
                "test_file_name": state["test_code_path"].name,
            }
        )

        return {
            **global_state,
            "diff": diff,
        }
