"""
DiffHunkのコンテキスト行を調整するモジュール。

DiffHunkは推測で選ばれた範囲であるため、ソースコードにないがdiff_linesにあるコンテキスト行が
含まれている場合があります。このモジュールは、そのようなコンテキスト行を"+"（追加行）に
調整する機能を提供します。

主な機能:
- DiffContextAdjuster: コンテキスト行を調整するクラス
- adjust_diff_context: DIFFのコンテキスト行を調整する関数
- adjust_diff_from_file: ファイルからDIFFのコンテキスト行を調整する関数

使用例:
    from utils.adjust_diff_context import adjust_diff_context
    
    # DIFFのコンテキスト行を調整
    adjusted_diff = adjust_diff_context(source_code, diff)
"""

from typing import List, Optional
import difflib
from utils.detect_diff_hunks import DiffHunk, DiffHunkProcessor


class DiffContextAdjuster:
    """
    DiffHunkのコンテキスト行を調整するクラス。
    ソースコードにないがdiff_linesにあるコンテキスト行を"+"に変換します。
    """
    
    def __init__(self, source_code: str):
        """
        DiffContextAdjusterを初期化します。
        
        Args:
            source_code: 元のソースコード
        """
        self.source_lines = source_code.split("\n")
    
    def adjust_hunk(self, hunk: DiffHunk) -> DiffHunk:
        """
        単一のDiffHunkのコンテキスト行を調整します。
        
        Args:
            hunk: 調整するDiffHunk
            
        Returns:
            調整されたDiffHunk
        """
        # ハンクの行番号情報を取得
        start_line = hunk.source_start_line
        end_line = hunk.source_end_line
        
        # 調整後のdiff行を格納するリスト
        adjusted_diff_lines = []
        
        # ソースコードの対応する範囲を取得
        source_segment = self.source_lines[start_line-1:end_line]
        source_index = 0
        
        for line in hunk.diff_lines:
            if not line:
                adjusted_diff_lines.append(line)
                continue
                
            if line.startswith(' '):  # コンテキスト行
                line_content = line[1:]  # 先頭の空白を削除
                
                # ソースコードの現在位置に対応する行があるか確認
                if source_index < len(source_segment):
                    source_line = source_segment[source_index]
                    
                    # 内容が一致するか確認（空白を無視）
                    if self._is_content_similar(source_line, line_content):
                        # 一致する場合はそのまま追加
                        adjusted_diff_lines.append(line)
                        source_index += 1
                    else:
                        # 一致しない場合は追加行として扱う
                        adjusted_diff_lines.append(f"+{line_content}")
                else:
                    # ソースコードの範囲外の場合は追加行として扱う
                    adjusted_diff_lines.append(f"+{line_content}")
            else:
                # 追加行または削除行はそのまま追加
                adjusted_diff_lines.append(line)
                
                # 削除行の場合はソースコードのインデックスを進める
                if line.startswith('-'):
                    source_index += 1
        
        # 調整後のDiffHunkを作成して返す
        return DiffHunk(adjusted_diff_lines, start_line, end_line)
    
    def _is_content_similar(self, left: str, right: str) -> bool:
        """
        2つの文字列の内容が類似しているかどうかを判断します。
        
        Args:
            left: 比較対象の文字列1
            right: 比較対象の文字列2
            
        Returns:
            内容が類似している場合はTrue
        """
        # 空白の違いを無視するために正規化
        left_normalized = left.strip()
        right_normalized = right.strip()
        
        # 完全一致の場合
        if left_normalized == right_normalized:
            return True
            
        # 一方が他方に含まれているか確認（コメントが追加されている可能性）
        # 短い文字列の誤判定を防ぐために5文字以上の場合にのみ適用
        if len(left_normalized) >= 5 and len(right_normalized) >= 5:
            if left_normalized in right_normalized or right_normalized in left_normalized:
                return True
        
        # SequenceMatcherで類似度を計算
        matcher = difflib.SequenceMatcher(None, left_normalized, right_normalized)
        similarity = matcher.ratio()
        
        # 類似度が0.85（85%）以上の場合は類似していると判断
        return similarity >= 0.85
    
    def adjust_hunks(self, hunks: List[DiffHunk]) -> List[DiffHunk]:
        """
        複数のDiffHunkのコンテキスト行を調整します。
        
        Args:
            hunks: 調整するDiffHunkのリスト
            
        Returns:
            調整されたDiffHunkのリスト
        """
        return [self.adjust_hunk(hunk) for hunk in hunks]


def adjust_diff_context(source_code: str, diff: str) -> str:
    """
    DIFFのコンテキスト行を調整します。
    
    Args:
        source_code: 元のソースコード
        diff: 調整するDIFF文字列
        
    Returns:
        調整後のDIFF文字列
    """
    # DIFFをハンクに分割
    processor = DiffHunkProcessor(source_code, diff)
    hunks = processor.hunking()
    
    # コンテキスト行を調整
    adjuster = DiffContextAdjuster(source_code)
    adjusted_hunks = adjuster.adjust_hunks(hunks)
    
    # 調整後のDIFFを生成
    adjusted_diff_lines = []
    
    # DIFFのヘッダー行を保持
    for line in diff.split("\n"):
        if line.startswith("---") or line.startswith("+++"):
            adjusted_diff_lines.append(line)
    
    # 調整後のハンクを追加
    for hunk in adjusted_hunks:
        # ハンクヘッダーを生成（簡易版）
        header = f"@@ -{hunk.source_start_line},{hunk.source_end_line - hunk.source_start_line + 1} +{hunk.source_start_line},{hunk.source_end_line - hunk.source_start_line + 1} @@"
        adjusted_diff_lines.append(header)
        
        # ハンクの内容を追加
        adjusted_diff_lines.extend(hunk.diff_lines)
    
    return "\n".join(adjusted_diff_lines)


# 使用例
def adjust_diff_from_file(source_path: str, diff: str) -> str:
    """
    ファイルからDIFFのコンテキスト行を調整します。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 調整するDIFF文字列
        
    Returns:
        調整後のDIFF文字列
    """
    # ソースコードを読み込み
    with open(source_path, 'r') as f:
        source_code = f.read()
    
    # DIFFのコンテキスト行を調整
    return adjust_diff_context(source_code, diff) 