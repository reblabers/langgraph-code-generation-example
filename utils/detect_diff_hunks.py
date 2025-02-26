from typing import List, Optional, Tuple
import re
import difflib

class DiffHunk:
    def __init__(self, diff_lines: List[str], source_start_line: int, source_end_line: int):
        """
        DIFFのハンクを表すクラスを初期化します。
        
        Args:
            diff_lines: DIFFの行のリスト（+, -, 空白で始まる行）
            source_start_line: ソースコードの開始行番号
            source_end_line: ソースコードの終了行番号
        """
        self.diff_lines = diff_lines
        self.source_start_line = source_start_line
        self.source_end_line = source_end_line

    def __str__(self):
        return f"Lines: {self.source_start_line}-{self.source_end_line}"


class DiffHunkProcessor:
    def __init__(self, code: str, diff: str):
        """DIFFを処理するためのクラスを初期化します。

        Args:
            code: 対応するソースコード
            diff: 分割するDIFF文字列
        """
        self.source_lines = code.split("\n")
        self.diff_lines = diff.split("\n") if diff else []
        # 標準的なdiffフォーマットの行番号情報を解析するための正規表現
        # 例: @@ -1,3 +1,3 @@ の形式
        self.hunk_header_pattern = re.compile(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

    def _is_diff_numbers_reliable(self, original_lines: List[str], expected_code_segment: List[str]) -> bool:
        """diffの行番号情報が信頼できるかどうかを判断します。

        Args:
            original_lines: ハンクから抽出した元のコードの行リスト
            expected_code_segment: ソースコードから抽出した期待される行リスト

        Returns:
            行番号情報が信頼できる場合はTrue、そうでない場合はFalse
        """
        # 空のリストの場合は信頼できないと判断
        if not original_lines or not expected_code_segment:
            return False
            
        # 最初と最後の行が完全一致しているか確認
        first_line_match = original_lines[0].strip() == expected_code_segment[0].strip()
        last_line_match = (len(original_lines) <= len(expected_code_segment) and 
                          original_lines[-1].strip() == expected_code_segment[len(original_lines)-1].strip())
        
        # 2つのコードの類似度を計算
        similarity = difflib.SequenceMatcher(None, 
                                           "\n".join(original_lines), 
                                           "\n".join(expected_code_segment[:len(original_lines)])).ratio()
        high_similarity = similarity > 0.8  # 80%以上の類似度を高いと判断
        
        # すべての条件を満たす場合のみ信頼できると判断
        return first_line_match and last_line_match and high_similarity

    def _find_best_match_position(self, original_lines: List[str]) -> Tuple[int, int]:
        """ソースコード内で最も一致度の高い位置を推測します。

        Args:
            original_lines: ハンクから抽出した元のコードの行リスト

        Returns:
            推測された開始行番号と行数のタプル
        """
        if not original_lines:
            raise ValueError("元のコードの行リストが空です")
            
        # まず最初の行が一致する位置を探す
        first_line = original_lines[0].strip()
        matching_positions = []
        
        for i, line in enumerate(self.source_lines):
            if line.strip() == first_line:
                matching_positions.append(i + 1)  # 1-indexedに変換
        
        if not matching_positions:
            # 最初の行が一致する位置がない場合は、類似度で探す
            best_start = 1
            best_score = 0
            
            for i in range(1, len(self.source_lines) + 1):
                end = min(i + len(original_lines), len(self.source_lines) + 1)
                segment = self.source_lines[i-1:end-1]
                segment = [line.strip() for line in segment]
                
                # 一致度を計算
                matcher = difflib.SequenceMatcher(None, 
                                                "\n".join(original_lines), 
                                                "\n".join(segment))
                score = matcher.ratio()
                
                if score > best_score:
                    best_score = score
                    best_start = i
            
            return best_start, len(original_lines)
        
        # 最初の行が一致する位置から、最も類似度の高い範囲を探す
        best_start = matching_positions[0]
        best_score = 0
        best_length = len(original_lines)
        
        for pos in matching_positions:
            # 最後の行が一致するか確認
            last_line_match = False
            for length in range(len(original_lines), min(len(original_lines) + 5, len(self.source_lines) - pos + 2)):
                if pos + length - 1 <= len(self.source_lines):
                    if (self.source_lines[pos + length - 2].strip() == 
                        original_lines[-1].strip()):
                        last_line_match = True
                        best_length = length
                        break
            
            # 範囲全体の類似度を計算
            end = min(pos + best_length - 1, len(self.source_lines))
            segment = self.source_lines[pos-1:end]
            segment = [line.strip() for line in segment]
            
            matcher = difflib.SequenceMatcher(None, 
                                            "\n".join(original_lines), 
                                            "\n".join(segment))
            score = matcher.ratio()
            
            # 最後の行が一致し、かつ類似度が高い場合は優先
            if last_line_match:
                score += 0.2  # 最後の行が一致する場合はスコアを加算
            
            if score > best_score:
                best_score = score
                best_start = pos
                if last_line_match:
                    best_length = length
        
        return best_start, best_length

    def verify_hunk_line_numbers(self, hunk_lines: List[str], source_start: int, source_length: int) -> Tuple[int, int]:
        """ハンクヘッダーから抽出した行番号情報を検証し、必要に応じて修正します。

        Args:
            hunk_lines: ハンクの行リスト
            source_start: ハンクヘッダーから抽出した開始行番号
            source_length: ハンクヘッダーから抽出した行数

        Returns:
            検証済みの開始行番号と行数のタプル
        """
        # ハンクから元のコードの行を抽出
        original_lines = []
        for line in hunk_lines:
            if line.startswith(" ") or line.startswith("-"):
                # 先頭の記号と空白を削除
                content = line[1:] if line.startswith(" ") else line[1:]
                original_lines.append(content)
        
        # 行番号情報が正しいか検証
        if source_start < 1 or source_start > len(self.source_lines):
            # 明らかに不正な行番号の場合は推測を実施
            return self._find_best_match_position(original_lines)
            
        # 期待されるコードセグメントを取得
        end_idx = min(source_start - 1 + source_length, len(self.source_lines))
        expected_code_segment = self.source_lines[source_start-1:end_idx]
        
        # diffの行番号情報が信頼できるかチェック
        if self._is_diff_numbers_reliable(original_lines, expected_code_segment):
            return source_start, source_length
        
        # 信頼できない場合は推測を実施
        try:
            return self._find_best_match_position(original_lines)
        except ValueError as e:
            # どうしようもない場合はデフォルト値を返す
            return 1, len(original_lines)

    def process_hunk(self, hunk_header: str, hunk_lines: List[str]) -> DiffHunk:
        """ハンクを処理し、DiffHunkオブジェクトを作成します。

        Args:
            hunk_header: ハンクのヘッダー行
            hunk_lines: ハンクの内容の行リスト

        Returns:
            作成されたDiffHunkオブジェクト
        """
        # 行番号情報を抽出
        match = self.hunk_header_pattern.match(hunk_header)
        
        if match:
            source_start = int(match.group(1))
            source_length = int(match.group(2))
        else:
            # 行番号情報を抽出できない場合はハンクの内容からソースコード内の最適な位置を推測
            # デフォルト値を初期値として使用
            source_start = 1
            source_length = len([line for line in hunk_lines if line.startswith(" ") or line.startswith("-")])
            
        # ハンクの内容からソースコード内の最適な位置を推測
        verified_start, verified_length = self.verify_hunk_line_numbers(
            hunk_lines, source_start, source_length
        )
        
        return DiffHunk(
            hunk_lines, 
            source_start_line=verified_start, 
            source_end_line=verified_start + verified_length - 1
        )

    def hunking(self) -> List[DiffHunk]:
        """DIFFをハンクに分割します。

        Returns:
            DIFFのハンクリスト
        """
        if not self.diff_lines:
            return []

        hunks = []
        current_hunk_lines = []
        current_hunk_header = None
        in_hunk = False
        
        i = 0
        while i < len(self.diff_lines):
            line = self.diff_lines[i]
            
            # diffのヘッダー行（--- や +++ で始まる行）はスキップ
            if line.startswith("---") or line.startswith("+++"):
                i += 1
                continue
                
            # 標準的なdiffフォーマットのハンクヘッダーを検出
            match = self.hunk_header_pattern.match(line)
            
            if match:
                # 前のハンクがあれば追加
                if current_hunk_lines and current_hunk_header:
                    hunks.append(self.process_hunk(current_hunk_header, current_hunk_lines))
                    current_hunk_lines = []
                
                # 新しいハンクの開始
                current_hunk_header = line
                in_hunk = True
                i += 1
                
                # ハンクの内容を収集
                while i < len(self.diff_lines):
                    line = self.diff_lines[i]
                    # 次のハンクヘッダーが見つかったら終了
                    if self.hunk_header_pattern.match(line):
                        break
                    # ハンクの内容を追加
                    current_hunk_lines.append(line)
                    i += 1
            else:
                # ハンクヘッダーでない場合はスキップ
                i += 1
        
        # 最後のハンクを追加
        if current_hunk_lines and current_hunk_header:
            hunks.append(self.process_hunk(current_hunk_header, current_hunk_lines))

        return hunks

    @classmethod
    def verify_line_numbers(cls, code_lines: List[str], hunk_lines: List[str], source_start: int, source_length: int) -> Tuple[int, int]:
        """行番号情報を検証するためのクラスメソッド。テスト用に公開されています。

        Args:
            code_lines: ソースコードの行リスト
            hunk_lines: ハンクの行リスト
            source_start: ハンクヘッダーから抽出した開始行番号
            source_length: ハンクヘッダーから抽出した行数

        Returns:
            検証済みの開始行番号と行数のタプル
        """
        processor = cls("\n".join(code_lines), "")
        return processor.verify_hunk_line_numbers(hunk_lines, source_start, source_length)


# 後方互換性のための関数
def verify_hunk_line_numbers(code_lines: List[str], hunk_lines: List[str], source_start: int, source_length: int) -> Tuple[int, int]:
    """ハンクヘッダーから抽出した行番号情報を検証し、必要に応じて修正します。
    
    注: 後方互換性のために残しています。新しいコードでは DiffHunkProcessor クラスを使用してください。

    Args:
        code_lines: ソースコードの行リスト
        hunk_lines: ハンクの行リスト
        source_start: ハンクヘッダーから抽出した開始行番号
        source_length: ハンクヘッダーから抽出した行数

    Returns:
        検証済みの開始行番号と行数のタプル
    """
    return DiffHunkProcessor.verify_line_numbers(code_lines, hunk_lines, source_start, source_length)


def hunking(code: str, diff: str) -> List[DiffHunk]:
    """DIFFをハンクに分割します。
    
    注: 後方互換性のために残しています。新しいコードでは DiffHunkProcessor クラスを使用してください。

    Args:
        code: 対応するソースコード
        diff: 分割するDIFF文字列

    Returns:
        DIFFのハンクリスト
    """
    processor = DiffHunkProcessor(code, diff)
    return processor.hunking()
