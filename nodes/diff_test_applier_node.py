from utils.diff_applier import apply_diff_to_file
from .state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict
from utils.repository import Repository
import shutil
import hashlib
import difflib
from typing import List
from nodes.state import Fault

class LocalState(TypedDict):
    source_code_path: Path
    test_code_path: Path
    faults: List[Fault]
    diff: str

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code_path=global_state["source_code_path"],
            test_code_path=global_state["test_code_path"],
            faults=global_state["faults"],
            diff=global_state["diff"],
        )


class DiffTestApplierNode:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)
        result = await self._process(state)
        result = result if result is not None else {}
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        # リポジトリをクリーン
        self.repository.clean()

        source_code_path = state["source_code_path"]
        test_code_path = state["test_code_path"]
        faults = state["faults"]

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

        try:
            # テストを実行. テストが失敗したら終了
            print("TESTING ON ORIGINAL")
            self.repository.test()
        except Exception as e:
            print(f"FAILED TEST: {e}")
            return None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_source_code_path = Path(temp_dir) / source_code_path.name
            shutil.copy(source_code_path, temp_source_code_path)

            # Faultsの埋め込み
            for fault in faults:
                mutated_source_path = apply_diff_to_file(
                    source_path=source_code_path,
                    diff=fault["diff"],
                )

                if mutated_source_path is None:
                    print("Failed to apply diff to source code")
                    return None

                # コードに適用
                shutil.copy(mutated_source_path, source_code_path)

                try:
                    # テストを実行. テストが失敗したら終了
                    print("TESTING ON FAULT")
                    self.repository.test()

                    print(f"Test passed as unexpected (fault not detected)")
                    return None
                except Exception as e:
                    print("Test failed as expected (fault detected)")

                # コードを元に戻す
                shutil.copy(temp_source_code_path, source_code_path)
        
        print("ALL FAULTS DETECTED")
        
        return None
