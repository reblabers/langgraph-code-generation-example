from typing import List, Optional, Tuple
import re
from .detect_diff_hunks import DiffHunk, DiffHunkProcessor


class MutantDiffGenerator:
    """MUTANTコメントを元にDIFFを作り直すクラス"""
    
    def __init__(self, hunks: List[DiffHunk]):
        """
        Args:
            hunks: DIFFのハンクリスト
        """
        self.hunks = hunks
        self.mutant_start_pattern = re.compile(r'.*// MUTANT <START>.*')
        self.mutant_end_pattern = re.compile(r'.*// MUTANT <END>.*')
        
    def _process_hunk_with_mutant_state(self, hunk: DiffHunk, is_mutating: bool) -> Tuple[DiffHunk, bool]:
        """ハンクをMUTANT状態に基づいて処理します。
        
        Args:
            hunk: 処理するDiffHunk
            is_mutating: 現在のMUTANT状態
            
        Returns:
            (処理後のDiffHunk, 次のハンクに引き継ぐMUTANT状態)のタプル
        """
        result_lines = []
        # ハンクヘッダーを保持
        for line in hunk.diff_lines:
            if line.startswith("@@"):
                result_lines.append(line)
                break
        
        # ハンク内の行を処理
        for line in hunk.diff_lines:
            # ヘッダー行はスキップ
            if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
                continue
                
            # 行の先頭の記号（+, -, 空白）を取得
            if line.strip():
                mark = line[0]
                content = line[1:].rstrip()
            else:
                mark = " "
                content = ""
                
            # MUTANT開始タグを検出
            if mark == "+" and self.mutant_start_pattern.match(content):
                is_mutating = True
                continue
                
            # MUTANT終了タグを検出
            if mark == "+" and self.mutant_end_pattern.match(content):
                is_mutating = False
                continue

            if mark == " ":
                # コンテキスト行はそのまま
                result_lines.append(line)
                continue
                
            # MUTANT状態に基づいて行を処理
            if is_mutating:
                if mark == "+" or mark == "-":
                    result_lines.append(line)
            else:
                # 通常状態では削除行（-）を優先
                if mark == "-":
                    # 削除行は空白行に変換
                    result_lines.append(" " + content)
                # 追加行（+）は無視
        
        # 新しいDiffHunkを作成
        new_hunk = DiffHunk(
            result_lines,
            hunk.source_start_line,
            hunk.source_end_line
        )
        
        return new_hunk, is_mutating
        
    def generate_hunks(self) -> List[DiffHunk]:
        """MUTANTコメントを元にDIFFを作り直します。
        
        Returns:
            新しいDiffHunkのリスト
        """
        if not self.hunks:
            return []
            
        result = []
        is_mutating = False  # 初期状態は非MUTANT
        has_mutant_tag = False
        
        # 各ハンクを順番に処理し、MUTANT状態を引き継ぐ
        for hunk in self.hunks:
            # ハンク内にMUTANTタグがあるか確認
            for line in hunk.diff_lines:
                if line.strip() and line[0] == "+" and (
                    self.mutant_start_pattern.match(line[1:].rstrip()) or 
                    self.mutant_end_pattern.match(line[1:].rstrip())
                ):
                    has_mutant_tag = True
                    break
            
            # ハンクを処理
            processed_hunk, is_mutating = self._process_hunk_with_mutant_state(hunk, is_mutating)
            result.append(processed_hunk)
        
        # MUTANTタグが存在しない場合は、元のハンクをそのまま返す
        if not has_mutant_tag:
            return self.hunks
            
        return result


def generate_mutant_diff(code: str, diff: str) -> str:
    """MUTANTコメントを元にDIFFを作り直します。
    
    Args:
        code: 対応するソースコード
        diff: 分割するDIFF文字列
        
    Returns:
        新しいDIFF文字列
    """
    processor = DiffHunkProcessor(code, diff)
    hunks = processor.hunking()
    generator = MutantDiffGenerator(hunks)
    
    # 新しいハンクを生成
    mutant_hunks = generator.generate_hunks()
    
    # ハンクからDIFF文字列を生成
    result = []
    for hunk in mutant_hunks:
        result.append("\n".join(hunk.diff_lines))
    
    return "\n".join(result)


def generate_mutant_diff_from_hunks(hunks: List[DiffHunk]) -> List[DiffHunk]:
    """MUTANTコメントを元にDIFFを作り直します。
    
    Args:
        hunks: DIFFのハンクリスト
        
    Returns:
        新しいDiffHunkのリスト
    """
    generator = MutantDiffGenerator(hunks)
    return generator.generate_hunks()
