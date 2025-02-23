import os
from pathlib import Path
import tempfile


def apply_diff_to_file(source_path: Path, diff: str) -> str:
    """
    DIFFをソースコードに適用して新しいファイルを生成します。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        生成されたファイルのパス
    """
    # 一時ファイルを作成
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = Path(temp_file.name)

    diff = diff.split("\n")
    
    # DIFFを適用
    with open(source_path, "r") as file:
        with open(temp_file_path, "w") as mutated_file:
            for line in diff:
                if not line.strip() or line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
                    continue

                mark = line[0]
                line = line[1:].rstrip()

                if mark == "+":
                    mutated_file.write(line)
                elif mark == "-":
                    original_line = next(file)
                else:
                    while True:
                        original_line = next(file)
                        if original_line.startswith(line):
                            mutated_file.write(original_line)
                            break
                        else:
                            mutated_file.write(original_line)
            
            for line in file:
                mutated_file.write(line)
    
    return temp_file_path
