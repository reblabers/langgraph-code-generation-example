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

        diff = self._rearrange_diff(state["diff"])

        # デバッグ用にdiffを保存
        with open("debug/last_diff_applier.diff", "w") as f:
            f.write(diff)

        diff_mutants = self._extract_diff_mutants(diff)

        diff_faults = []
        for diff_mutant in diff_mutants:
            # リポジトリをクリーン
            self.repository.clean()

            # import pprint
            # pprint.pprint(source_code_path)
            # pprint.pprint(diff_mutant)
            
            mutated_path = apply_diff_to_file_for_mutant(
                source_path=source_code_path,
                diff=diff_mutant,
            )

            if mutated_path is None:
                print("Failed to apply diff to file", diff_mutant)
                continue

            # コードに適用
            shutil.copy(mutated_path, source_code_path)

            try:
                # テストを実行. テストが失敗したら終了
                self.repository.test()
            except Exception as e:
                print(f"SKIPPED: {e}")
                continue

            try:
                # フォーマットを実行
                self.repository.format()
            except Exception as e:
                pass

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

    def _rearrange_diff(self, diff: str) -> str:
        difflines = diff.splitlines()
        for index in range(len(difflines)):
            if "// MUTANT <START>" in difflines[index]:
                comment_line = difflines[index]
                i = index
                while True:
                    if not difflines[i - 1].startswith("-"):
                        break
                    difflines[i] = difflines[i - 1]
                    i -= 1
                difflines[i] = comment_line
        return "\n".join(difflines)
         
    def _extract_diff_mutants(self, diff: str) -> List[str]:
        """diffから各MUTANTブロックのdiffのリストを生成します。
        各MUTANTブロックは、STARTタグから次のSTART/END/EOFまでを対象とします。

        Args:
            diff (str): 元のdiffテキスト

        Returns:
            List[str]: 各MUTANTブロックに対応するdiffのリスト。
                      各ブロックは以下の規則で生成されます：
                      - STARTタグを基準に、次のSTART/END/EOFまでを対象とする
                      - 他のMUTANTブロックは全てSKIPに置換される
                      - 変更前のコードが先に出力され、その後に変更後のコードが出力される
        """
        # MUTANTタグの数をチェック
        if diff.count("MUTANT <START>") == 0:
            return []

        # MUTANTブロックの位置を特定
        def find_all_indexes(text: str, pattern: str, start: int = 0) -> List[int]:
            """文字列内の全てのパターンの位置を取得します"""
            indexes = []
            while True:
                index = text.find(pattern, start)
                if index == -1:
                    break
                indexes.append(index)
                start = index + len(pattern)
            return indexes

        # 全てのSTARTタグの位置を取得
        start_indexes = find_all_indexes(diff, "MUTANT <START>")
        print(f"start_indexes: {start_indexes}")

        # 各STARTタグに対応する終了位置と終了タイプを特定
        end_indexes = []
        for start in start_indexes:
            current_pos = start + len("MUTANT <START>")
            next_start = diff.find("MUTANT <START>", current_pos)
            next_end = diff.find("MUTANT <END>", current_pos)

            # 終了タイプを決定（END/START/EOF）
            if next_start == -1 and next_end == -1:
                # 次のタグが見つからない場合はEOFまで
                end = len(diff)
                end_type = "EOF"
            elif next_start == -1 or (next_end != -1 and next_end < next_start):
                # ENDタグが先に見つかった場合
                end = next_end + len("MUTANT <END>")
                end_type = "END"
            else:
                # STARTタグが先に見つかった場合
                end = next_start + len("MUTANT <START>")
                end_type = "START"
            
            end_indexes.append((end, end_type))

        # 各MUTANTブロックのdiffを生成
        final_diffs = []
        for start, (end, end_type) in zip(start_indexes, end_indexes):
            # 前のブロックをSKIPに置換
            before = diff[:start].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")

            # 終了タイプに応じてブロックを処理
            if end_type == "END":
                # ENDで終了する場合は、そのまま使用
                mutant = diff[start:end]
            elif end_type == "START":
                # STARTで終了する場合は、STARTをENDに置換
                mutant = diff[start:end-len("MUTANT <START>")] + "MUTANT <END>"
            else:  # EOF
                # EOFで終了する場合は、残り全てを使用
                mutant = diff[start:]

            # 後続のブロックをSKIPに置換
            after = diff[end:].replace("MUTANT <START>", "MUTANT <SKIP>").replace("MUTANT <END>", "MUTANT <SKIP>")

            final_diffs.append(before + mutant + after)

        return final_diffs
