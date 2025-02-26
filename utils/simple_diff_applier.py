from typing import List, Optional, Tuple
import logging
from utils.detect_diff_hunks import DiffHunk

# ロガーの設定
logger = logging.getLogger(__name__)


def apply_hunk(source_code: str, hunk: DiffHunk) -> str:
    """
    単一のDiffHunkをソースコードに適用します。
    
    Args:
        source_code: 元のソースコード
        hunk: 適用するDiffHunk
        
    Returns:
        変更後のソースコード
    """
    # ソースコードを行に分割
    source_lines = source_code.split('\n')
    
    # 変更後のコードを格納するリスト
    result_lines = []
    
    # ハンクの行番号情報を取得
    start_line = hunk.source_start_line
    end_line = hunk.source_end_line
    
    # 行番号が範囲外の場合は例外を発生
    if start_line < 1 or end_line > len(source_lines):
        raise ValueError(f"ハンクの行番号が範囲外です: {start_line}-{end_line}, ファイル行数: {len(source_lines)}")
    
    # ハンク適用前の行を追加
    result_lines.extend(source_lines[:start_line - 1])
    
    # ハンクの内容を処理
    current_source_line = start_line - 1  # 0-indexedに変換
    
    # ハンクの内容に基づいて変更を適用
    for line in hunk.diff_lines:  # linesからdiff_linesに変更
        if not line:
            continue
            
        if line.startswith(' '):  # コンテキスト行
            # ソースコードの対応する行と一致するか確認
            if current_source_line < len(source_lines):
                source_line = source_lines[current_source_line]
                line_content = line[1:]  # 先頭の空白を削除
                
                # 内容が一致しない場合は警告
                if not _is_content_similar(source_line, line_content):
                    logger.warning(f"コンテキスト行が一致しません: '{source_line}' != '{line_content}'")
                
                result_lines.append(source_line)
                current_source_line += 1
            else:
                logger.warning("ソースコードの行数が足りません")
                break
                
        elif line.startswith('-'):  # 削除行
            # 対応する行をスキップ
            if current_source_line < len(source_lines):
                line_content = line[1:]  # 先頭の'-'を削除
                source_line = source_lines[current_source_line]
                
                # 内容が一致しない場合は警告
                if not _is_content_similar(source_line, line_content):
                    logger.warning(f"削除行が一致しません: '{source_line}' != '{line_content}'")
                
                current_source_line += 1
            else:
                logger.warning("ソースコードの行数が足りません")
                break
                
        elif line.startswith('+'):  # 追加行
            # 新しい行を追加
            line_content = line[1:]  # 先頭の'+'を削除
            result_lines.append(line_content)
    
    # ハンク適用後の残りの行を追加
    if current_source_line < len(source_lines):
        result_lines.extend(source_lines[current_source_line:])
    
    # 結果を文字列として返す
    return '\n'.join(result_lines)


def _is_content_similar(left: str, right: str) -> bool:
    """
    2つの文字列の内容が類似しているかどうかを判断します。
    空白を無視して比較します。
    
    Args:
        left: 比較対象の文字列1
        right: 比較対象の文字列2
        
    Returns:
        内容が類似している場合はTrue
    """
    # 空白を削除して比較
    left_normalized = left.strip().replace(' ', '')
    right_normalized = right.strip().replace(' ', '')
    
    return left_normalized == right_normalized


def _calculate_line_changes(before_code: str, after_code: str) -> Tuple[int, int]:
    """
    変更前後のコードの行数の変化を計算します。
    
    Args:
        before_code: 変更前のコード
        after_code: 変更後のコード
        
    Returns:
        (追加された行数, 削除された行数)のタプル
    """
    before_lines = before_code.split('\n')
    after_lines = after_code.split('\n')
    
    added_lines = max(0, len(after_lines) - len(before_lines))
    deleted_lines = max(0, len(before_lines) - len(after_lines))
    
    return added_lines, deleted_lines


def apply_hunks(source_code: str, hunks: List[DiffHunk]) -> str:
    """
    複数のDiffHunkをソースコードに順番に適用します。
    
    Args:
        source_code: 元のソースコード
        hunks: 適用するDiffHunkのリスト
        
    Returns:
        変更後のソースコード
    """
    # ハンクを行番号順にソート
    sorted_hunks = sorted(hunks, key=lambda h: h.source_start_line)
    
    # 各ハンクを順番に適用
    result = source_code
    
    # 行番号の調整用の変数
    line_offset = 0
    
    for i, hunk in enumerate(sorted_hunks):
        # ハンクの行番号を調整
        if line_offset != 0:
            # 新しいハンクオブジェクトを作成して行番号を調整
            adjusted_hunk = DiffHunk(
                hunk.diff_lines,  # linesからdiff_linesに変更
                hunk.source_start_line + line_offset,
                hunk.source_end_line + line_offset
            )
        else:
            adjusted_hunk = hunk
        
        # 変更前のコードを保存
        before_code = result
        
        # ハンクを適用
        result = apply_hunk(result, adjusted_hunk)
        
        # 行数の変化を計算
        # TODO: resultから計算する。diffが正しいと信頼しない
        # 実際の変更前後のコードから行数の変化を計算
        added_lines, deleted_lines = _calculate_line_changes(before_code, result)
        line_offset += (added_lines - deleted_lines)
    
    return result


def apply_diff_from_file(source_path: str, diff: str) -> str:
    """
    DIFFをファイルに適用します。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        変更後のソースコード
    """
    from utils.detect_diff_hunks import DiffHunkProcessor
    
    # ソースコードを読み込み
    with open(source_path, 'r') as f:
        source_code = f.read()
    
    # DIFFをハンクに分割
    processor = DiffHunkProcessor(source_code, diff)
    hunks = processor.hunking()
    
    # ハンクを適用
    return apply_hunks(source_code, hunks) 