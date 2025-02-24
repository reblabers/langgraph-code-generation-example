from utils.diff_applier import apply_diff_to_file_for_mutant
from .state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict
from utils.repository import Repository
import shutil
import hashlib


class LocalState(TypedDict):
    source_code_path: Path
    diff: str

    @staticmethod
    def load_from(global_state: GlobalState) -> "LocalState":
        return LocalState(
            source_code_path=global_state["source_code_path"],
            diff=global_state["diff"],
        )


class DiffApplierNode:
    def __init__(self, repository: Repository):
        self.repository = repository

    async def process(self, global_state: GlobalState) -> GlobalState:
        state = LocalState.load_from(global_state)

        # リポジトリをクリーン
        self.repository.clean()

        source_code_path = state["source_code_path"]
        source_code_hash = hashlib.sha256(source_code_path.read_text().encode()).hexdigest()

        diff = state["diff"]

        # diffにある `MUTANT <START>` と `MUTANT <END>` の間の行のdiffだけを適用
        mutant_start_count = diff.count("MUTANT <START>")
        mutant_end_count = diff.count("MUTANT <END>")
        if mutant_start_count != mutant_end_count:
            raise Exception("MUTANT <START>とMUTANT <END>の数が一致しません: start={mutant_start_count}, end={mutant_end_count}")

        start = 0
        start_indexes = []
        length = len("MUTANT <START>")
        for _ in range(mutant_start_count):
            index = diff.find("MUTANT <START>", start)
            start_indexes.append(index)
            start = index + length

        start = 0
        end_indexes = []
        length = len("MUTANT <END>")
        for _ in range(mutant_end_count):
            index = diff.find("MUTANT <END>", start)
            end_indexes.append(index + length)
            start = index + length

        print(f"start_indexes: {start_indexes}")
        print(f"end_indexes: {end_indexes}")

        for i in range(mutant_start_count):
            start = start_indexes[i]
            end = end_indexes[i]

            before = diff[:start].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")
            mutant = diff[start:end]
            after = diff[end:].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")
            
            final_diff = before + mutant + after

            # リポジトリをクリーン
            self.repository.clean()

            mutated_path = apply_diff_to_file_for_mutant(
                source_path=source_code_path,
                diff=final_diff,
            )

            if mutated_path is None:
                print("Failed to apply diff to file", final_diff)
                continue

            # コードに適用
            shutil.copy(mutated_path, state["source_code_path"])

            try:
                # テストを実行. テストが失敗したら終了
                self.repository.test()

                # フォーマットを実行    
                self.repository.format()
            except Exception as e:
                print(f"SKIPPED: {e}")
                continue

            # 変更後のソースコードのハッシュ値を記録
            mutated_code_hash = hashlib.sha256(mutated_path.read_text().encode()).hexdigest()
            if source_code_hash == mutated_code_hash:
                print("SKIPPED: ソースコードが変更されていません")
                continue

            print("SUCCESS")
            print(f"final_diff: {final_diff}")
            print("########################")

        return {
            **global_state,
            # "mutated_code": mutated_code,
            # "is_equivalent": source_code_hash == mutated_code_hash,
        }
