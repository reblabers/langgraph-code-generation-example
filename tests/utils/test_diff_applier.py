import pytest
from pathlib import Path
from utils.diff_applier import apply_diff_to_file, apply_diff_to_file_for_mutant
import tempfile
import os

class TestDiffApplier:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """テストの前処理：一時ディレクトリの作成"""
        self.test_dir = tmp_path
        yield
        # クリーンアップは pytest が自動的に行う

    def write_source(self, content: str, filename: str = "test.py") -> Path:
        """テストファイルにソースコードを書き込む
        
        Args:
            content: 書き込むソースコード
            filename: 作成するファイル名（デフォルト: test.py）
        
        Returns:
            作成したファイルのパス
        """
        path = self.test_dir / filename
        path.write_text(content, encoding='utf-8')
        return path

    def test_basic_diff_application(self):
        """基本的なDIFF適用のテスト"""
        # 元のコード
        source = """def hello():
    print("Hello")
    print("World")
"""
        # DIFFの内容
        diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello():
-    print("Hello")
+    print("Hello!!!")
     print("World")
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        expected = """def hello():
    print("Hello!!!")
    print("World")
"""
        assert result == expected

    def test_mutant_diff_application(self):
        """ミュータント部分の変更が正しく適用されることを確認"""
        source = """def calculate(x, y):
    return x + y
"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,4 @@
 def calculate(x, y):
+    // MUTANT <START>
-    return x + y
+    return x - y
+    // MUTANT <END>
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        expected = """def calculate(x, y):
    return x - y
"""
        assert result == expected

    def test_mutant_diff_ignores_outside_changes(self):
        """ミュータントタグの外側の変更は無視されることを確認"""
        source = """def calculate(x, y):
    print("start")
    return x + y
    print("end")
"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
-def calculate(x, y):
+def calc(x, y):
     print("start")
+    // MUTANT <START>
-    return x + y
+    return x - y
+    // MUTANT <END>
-    print("end")
+    print("finished")
"""
        source_path = self.write_source(source)
        
        # apply_diff_to_file_for_mutant ではミュータント部分のみ変更される
        result_path = apply_diff_to_file_for_mutant(source_path, diff)
        assert result_path is not None
        result = result_path.read_text()
        expected_mutant = """def calculate(x, y):
    print("start")
    return x - y
    print("end")
"""
        assert result == expected_mutant
