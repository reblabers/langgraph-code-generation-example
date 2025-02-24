from utils.diff_applier import apply_diff_to_file_for_mutant
from .state import GlobalState
from pathlib import Path
from typing_extensions import TypedDict
from utils.repository import Repository
import shutil
import hashlib
import difflib
from typing import List


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
        result = await self._process(state)
        return {**global_state, **result}

    async def _process(self, state: LocalState):
        # リポジトリをクリーン
        self.repository.clean()

        source_code_path = state["source_code_path"]
        source_code = source_code_path.read_text()
        source_code_hash = hashlib.sha256(source_code.encode()).hexdigest()

        diff_mutants = self._extract_diff_mutants(state["diff"])

        diff_faults = []
        for diff_mutant in diff_mutants:
            # リポジトリをクリーン
            self.repository.clean()

            mutated_path = apply_diff_to_file_for_mutant(
                source_path=source_code_path,
                diff=diff_mutant,
            )

            if mutated_path is None:
                print("Failed to apply diff to file", diff_mutant)
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
            mutated_code = mutated_path.read_text()
            mutated_code_hash = hashlib.sha256(mutated_code.encode()).hexdigest()
            if source_code_hash == mutated_code_hash:
                print("SKIPPED: ソースコードが変更されていません")
                continue

            # source_code_pathとmutated_pathのdiffを作り直す
            new_diff = difflib.unified_diff(source_code.splitlines(), mutated_code.splitlines(), lineterm="")
            diff_faults.append("\n".join(new_diff))

        return {
            "diff_faults": diff_faults,
        }

    def _extract_diff_mutants(self, diff: str) -> List[str]:
        """diffから各MUTANTブロックのdiffのリストを生成します。

        Args:
            diff (str): 元のdiffテキスト

        Returns:
            List[str]: 各MUTANTブロックに対応するdiffのリスト
        
        Raises:
            Exception: MUTANT <START>とMUTANT <END>の数が一致しない場合
            Exception: ネストされたMUTANTブロックが検出された場合
            Exception: MUTANTブロックの範囲が無効な場合
        """
        # MUTANTタグの数をチェック
        mutant_start_count = diff.count("MUTANT <START>")
        # if mutant_start_count != mutant_end_count:
        #     raise Exception(f"MUTANT <START>とMUTANT <END>の数が一致しません: start={mutant_start_count}, end={mutant_end_count}")
        
        if mutant_start_count == 0:
            return []

        # MUTANTブロックの位置を特定
        def find_all_indexes(text: str, pattern: str, start: int = 0) -> List[int]:
            indexes = []
            while True:
                index = text.find(pattern, start)
                if index == -1:
                    break
                indexes.append(index)
                start = index + len(pattern)
            return indexes

        start_indexes = find_all_indexes(diff, "MUTANT <START>")
        # end_indexes = [i + len("MUTANT <END>") for i in find_all_indexes(diff, "MUTANT <END>")]

        print(f"start_indexes: {start_indexes}")
        # print(f"end_indexes: {end_indexes}")

        end_indexes = []
        # MUTANTブロックの範囲をチェック
        for i in range(len(start_indexes)):
            start = start_indexes[i]
            current_pos = start + len("MUTANT <START>")
            
            # start以降のMUTANT <START>, MUTANT <END>, EOFを探す
            next_start = diff.find("MUTANT <START>", current_pos)
            next_end = diff.find("MUTANT <END>", current_pos)
            
            # 次のシンボルを決定
            if next_start == -1 and next_end == -1:
                # EOFで終了
                end = len(diff)
                end_indexes.append((end, "EOF"))
            elif next_start == -1 or (next_end != -1 and next_end < next_start):
                # ENDで終了
                end = next_end + len("MUTANT <END>")
                end_indexes.append((end, "END"))
            else:
                # STARTで終了
                end = next_start + len("MUTANT <START>")
                end_indexes.append((end, "START"))

        # 各MUTANTブロックに対してfinal_diffを生成
        final_diffs = []
        for i in range(len(start_indexes)):
            start = start_indexes[i]
            end, end_type = end_indexes[i]

            # 前後のコンテキストを保持しつつ、他のMUTANTブロックをSKIPに置換
            before = diff[:start].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")
            
            # 終了位置のシンボルに合わせて書き換え方を変える
            if end_type == "END":
                # ENDで終了 - そのまま、他をSKIPに置換
                mutant = diff[start:end]
                after = diff[end:].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")
            elif end_type == "START":
                # STARTで終了 - ENDを追加
                mutant = diff[start:end]
                # mutantの最後7文字を<END>に変換
                mutant = mutant[:-7] + "<END>"
                after = diff[end:].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")
            else:  # EOF
                # EOFで終了 - そのまま
                mutant = diff[start:]
                after = ""
            
            final_diffs.append(before + mutant + after)

        return final_diffs
