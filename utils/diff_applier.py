import os
from pathlib import Path
import tempfile
from typing import Optional, List, Tuple
from utils.detect_diff_hunks import DiffHunkProcessor
from utils.simple_diff_applier import apply_hunks
from utils.mutant_diff_generator import generate_mutant_diff_from_hunks
from utils.adjust_diff_context import DiffContextAdjuster


def apply_diff_to_file(source_path: Path, diff: str) -> Optional[Path]:
    """
    DIFFをソースコードに適用して新しいファイルを生成します。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        生成されたファイルのパス
    """
    # ソースコードを読み込み
    with open(source_path, 'r') as f:
        source_code = f.read()
    
    # DIFFをハンクに分割
    processor = DiffHunkProcessor(source_code, diff)
    hunks = processor.hunking()
    
    # コンテキスト行を調整
    adjuster = DiffContextAdjuster(source_code)
    adjusted_hunks = adjuster.adjust_hunks(hunks)
    
    # ハンクを適用
    result_code = apply_hunks(source_code, adjusted_hunks)
    
    # 結果を一時ファイルに書き込み
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = Path(temp_file.name)
    
    with open(temp_file_path, 'w') as f:
        f.write(result_code)
    
    return temp_file_path


def apply_diff_to_file_for_mutant(source_path: Path, diff: str) -> Optional[Path]:
    """
    DIFFをソースコードに適用して新しいファイルを生成します（MUTANTモード）。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        生成されたファイルのパス
    """
    # ソースコードを読み込み
    with open(source_path, 'r') as f:
        source_code = f.read()
    
    # DIFFをハンクに分割
    processor = DiffHunkProcessor(source_code, diff)
    hunks = processor.hunking()
    
    # コンテキスト行を調整
    adjuster = DiffContextAdjuster(source_code)
    adjusted_hunks = adjuster.adjust_hunks(hunks)
    
    # MUTANTコメントを元にハンクを作り直す
    mutant_hunks = generate_mutant_diff_from_hunks(adjusted_hunks)
    
    # ハンクを適用
    result_code = apply_hunks(source_code, mutant_hunks)
    
    # 結果を一時ファイルに書き込み
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = Path(temp_file.name)
    
    with open(temp_file_path, 'w') as f:
        f.write(result_code)
    
    return temp_file_path
