import os
from pathlib import Path
import tempfile


def apply_diff_to_file(source_path: Path, diff: str) -> Path | None:
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
    try:
        confident = False
        with open(source_path, "r") as file:
            with open(temp_file_path, "w") as mutated_file:
                for diffline in diff:
                    if diffline.startswith("@@"):
                        confident = False
                        continue

                    if not diffline.strip() or diffline.startswith("---") or diffline.startswith("+++"):
                        continue

                    mark = diffline[0]
                    diffline = diffline[1:].rstrip()

                    if mark == "+":
                        mutated_file.write(diffline + "\n")
                    elif mark == "-":
                        if confident:
                            original_line = next(file)
                        else:
                            while True:
                                original_line = next(file)
                                if original_line.strip().startswith(diffline.strip()):
                                    break
                    else:
                        while True:
                            original_line = next(file)
                            if original_line.strip().startswith(diffline.strip()):
                                confident = True
                                mutated_file.write(original_line)
                                break
                            else:
                                mutated_file.write(original_line)
                
                for original_line in file:
                    mutated_file.write(original_line)

    except StopIteration:
        temp_file_path.unlink()
        return None
    
    return temp_file_path
