from utils.diff_applier import apply_diff_to_file
from .state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict
from utils.repository import Repository
import shutil
import hashlib


class LocalState(TypedDict):
    diff: str
    source_code_path: Path

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            diff=global_state["diff"],
            source_code_path=global_state["source_code_path"],
        )


class DiffApplierNode:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)

        source_code_path = state["source_code_path"]
        mutated_path = apply_diff_to_file(
            source_path=source_code_path,
            diff=state["diff"],
        )

        if mutated_path is None:
            print("diff = ", state["diff"])
            raise Exception("Failed to apply diff to file")

        # リポジトリをクリーン
        self.repository.clean()

        # 変更前のソースコードのハッシュ値を記録
        source_code_hash = hashlib.sha256(source_code_path.read_text().encode()).hexdigest()

        # コードに適用
        shutil.copy(mutated_path, state["source_code_path"])

        # テストを実行. テストが失敗したら終了
        self.repository.test()

        # フォーマットを実行    
        self.repository.format()

        # 変更後のソースコードのハッシュ値を記録
        mutated_code_hash = hashlib.sha256(mutated_path.read_text().encode()).hexdigest()

        with open(mutated_path) as f:
            mutated_code = f.read()

        return {
            **global_state,
            "mutated_code": mutated_code,
            "is_equivalent": source_code_hash == mutated_code_hash,
        }
