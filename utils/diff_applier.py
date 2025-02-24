import os
from pathlib import Path
import tempfile
from typing import Optional


class DiffApplier:
    """DIFFをソースコードに適用するクラス"""
    
    def __init__(self, source_path: Path):
        """
        Args:
            source_path: 元のソースコードのパス
        """
        self.source_path = source_path
        self._confident = False
        self._mutating: Optional[bool] = None
        
    def _create_temp_file(self) -> Path:
        """一時ファイルを作成します"""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        return Path(temp_file.name)
    
    def _is_mutant_mode(self) -> bool:
        """MUTANTモードかどうかを判定します"""
        return self._mutating is not None

    def _is_normal_mode(self) -> bool:
        """通常モード（非MUTANTモード）かどうかを判定します"""
        return not self._is_mutant_mode()
    
    def _process_diff_line(
        self,
        diffline: str,
        file,
        mutated_file,
    ) -> None:
        """DIFFの1行を処理します。

        Args:
            diffline: 処理対象のDIFF行
            file: 元のソースコードのファイルオブジェクト
            mutated_file: 変更後のコードを書き込むファイルオブジェクト
        """
        # 1. DIFFのヘッダー行（@@で始まる行）の場合、confidentをFalseにリセット
        if diffline.startswith("@@"):
            self._confident = False
            return

        # 2. 空行やDIFFのメタ情報行（---/+++）は無視
        if diffline.startswith("---") or diffline.startswith("+++"):
            return

        if diffline.strip():
            mark = diffline[0]
            diffline = diffline[1:].rstrip()
        else:
            mark = " "
            diffline = ""

        # 3. 追加行（+で始まる行）の処理
        #    - MUTANTモードの場合、MUTANT範囲のみ処理
        #    - 通常モードの場合、すべての追加行を処理
        if mark == "+":
            if self._is_mutant_mode():
                if "// MUTANT <START>" in diffline:
                    self._mutating = True
                    return
                if "// MUTANT <END>" in diffline:
                    self._mutating = False
                    return
                if not self._mutating:
                    return
            mutated_file.write(diffline + "\n")

        # 4. 削除行（-で始まる行）の処理
        #    - MUTANTモードでMUTANT範囲内、または通常モードの場合のみ処理
        #    - 元ファイルから対応する行をスキップ
        #       - 一致しない場合は、元ファイルの行をそのまま書き込む
        elif (mark == "-" and (self._is_normal_mode() or self._mutating)):
            if self._confident:
                next(file)
            else:
                while True:
                    original_line = next(file)
                    if original_line.strip().startswith(diffline.strip()):
                        if 5 <= len(original_line.strip()):
                            # 5文字以上の行で一致した場合は信頼する
                            self._confident = True
                        break
                    else:
                        mutated_file.write(original_line)

        # 5. コンテキスト行（変更なしの行）の処理
        #    - 元ファイルから対応する行を探して書き込み
        #    - 見つかった場合はconfidentをTrueに設定
        else:
            while True:
                original_line = next(file)
                if original_line.strip().startswith(diffline.strip()):
                    if not self._confident and 5 <= len(original_line.strip()):
                        # 5文字以上の行で一致した場合は信頼する
                        self._confident = True
                    mutated_file.write(original_line)
                    break
                else:
                    mutated_file.write(original_line)

    def apply_diff(self, diff: str, mutant_mode: bool = False) -> Optional[Path]:
        """
        DIFFをソースコードに適用して新しいファイルを生成します。
        
        Args:
            diff: 適用するDIFF文字列
            mutant_mode: MUTANTモードを有効にするかどうか
            
        Returns:
            生成されたファイルのパス
        """
        temp_file_path = self._create_temp_file()
        diff_lines = diff.split("\n")

        while diff_lines:
            line = diff_lines[0].strip()
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@@"):
                break
            diff_lines.pop(0)
        
        while diff_lines:
            line = diff_lines[-1].strip()
            if line and line != "```":
                break
            diff_lines.pop(-1)

        try:
            self._confident = False
            self._mutating = None if not mutant_mode else False
            
            with open(self.source_path, "r") as file:
                with open(temp_file_path, "w") as mutated_file:
                    for diffline in diff_lines:
                        self._process_diff_line(diffline, file, mutated_file)
                    
                    # 残りの行をコピー
                    for original_line in file:
                        mutated_file.write(original_line)

        except StopIteration:
            temp_file_path.unlink()
            return None
        
        return temp_file_path


def apply_diff_to_file(source_path: Path, diff: str) -> Optional[Path]:
    """
    DIFFをソースコードに適用して新しいファイルを生成します。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        生成されたファイルのパス
    """
    applier = DiffApplier(source_path)
    return applier.apply_diff(diff)


def apply_diff_to_file_for_mutant(source_path: Path, diff: str) -> Optional[Path]:
    """
    DIFFをソースコードに適用して新しいファイルを生成します（MUTANTモード）。
    
    Args:
        source_path: 元のソースコードのパス
        diff: 適用するDIFF文字列
        
    Returns:
        生成されたファイルのパス
    """
    applier = DiffApplier(source_path)
    return applier.apply_diff(diff, mutant_mode=True)
