import pytest
from pathlib import Path
from utils.diff_applier import apply_diff_to_file, apply_diff_to_file_for_mutant

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
        
        # apply_diff_to_file では全ての変更が適用される
        source_path = self.write_source(source)  # ファイルを元の状態に戻す
        result_path = apply_diff_to_file(source_path, diff)
        assert result_path is not None
        result = result_path.read_text()
        expected_full = """def calc(x, y):
    print("start")
    // MUTANT <START>
    return x - y
    // MUTANT <END>
    print("finished")
"""
        assert result == expected_full

    def test_invalid_diff(self):
        source = "print('test')\n"
        diff = "invalid diff content"
        
        source_path = self.write_source(source, "invalid.py")
        result_path = apply_diff_to_file(source_path, diff)
        
        assert result_path is None

    def test_empty_diff(self):
        source = "print('test')\n"
        diff = ""
        
        source_path = self.write_source(source, "empty.py")
        result_path = apply_diff_to_file(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        assert result == source 

    def test_multiple_mutant_blocks(self):
        """複数のミュータントブロックがある場合、それぞれが独立して適用されることを確認"""
        source = """def calculate(x, y):
    result = x + y
    print(result)
    return result
"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
-def calculate(x, y):
+def calc(x, y):
+    // MUTANT <START>
-    result = x + y
+    result = x - y
+    // MUTANT <END>
     print(result)
+    // MUTANT <START>
-    return result
+    return result * 2
+    // MUTANT <END>
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        expected = """def calculate(x, y):
    result = x - y
    print(result)
    return result * 2
"""
        assert result == expected

    def test_incomplete_mutant_tags(self):
        """不完全なミュータントタグがある場合、その部分の変更は適用されないことを確認"""
        source = """def process(data):
    x = 1
    y = 2
    return x + y
"""
        # 開始タグのみ
        diff1 = """--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
     // MUTANT <START>
-    x = 1
+    x = 10
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff1)
        assert result_path is None

        # 終了タグのみ
        diff2 = """--- a/test.py
+++ b/test.py
@@ -1,4 +1,4 @@
-    x = 1
+    x = 10
     // MUTANT <END>
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff2)
        assert result_path is None

    def test_multi_line_mutant_changes(self):
        """ミュータントブロック内で複数行の変更がある場合を確認"""
        source = """def process_list(items):
    result = []
    for item in items:
        result.append(item)
    return result
"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,7 @@
 def process_list(items):
+    // MUTANT <START>
-    result = []
-    for item in items:
-        result.append(item)
+    result = set()
+    for i, item in enumerate(items):
+        if i % 2 == 0:
+            result.add(item)
+    // MUTANT <END>
     return result
"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        expected = """def process_list(items):
    result = set()
    for i, item in enumerate(items):
        if i % 2 == 0:
            result.add(item)
    return result
"""
        assert result == expected

    def test_mutant_at_file_boundaries(self):
        """ファイルの先頭や末尾でのミュータント適用を確認"""
        source = """x = 1
y = 2
z = 3
"""
        # ファイル先頭のミュータント
        diff1 = """--- a/test.py
+++ b/test.py
@@ -1,1 +1,2 @@
+    // MUTANT <START>
-x = 1
+x = 100
+    // MUTANT <END>
 y = 2
 z = 3"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff1)
        assert result_path is not None
        result = result_path.read_text()
        expected1 = """x = 100
y = 2
z = 3
"""
        assert result == expected1

        # ファイル末尾のミュータント
        diff2 = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 x = 1
 y = 2
+    // MUTANT <START>
-z = 3
+z = 300
+    // MUTANT <END>"""
        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff2)
        assert result_path is not None
        result = result_path.read_text()
        expected2 = """x = 1
y = 2
z = 300
"""
        assert result == expected2

    def test_mutant_start_without_end(self):
        """STARTタグのみで終了タグがない場合、最後までが変更対象として扱われることを確認"""
        source = """def process(data):
    x = 1
    y = 2
    z = 3
    return x + y + z
"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def process(data):
     x = 1
+    // MUTANT <START>
-    y = 2
-    z = 3
-    return x + y + z
+    y = 20
+    z = 30
+    return x * y * z
"""

        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff)
        
        assert result_path is not None
        result = result_path.read_text()
        expected = """def process(data):
    x = 1
    y = 20
    z = 30
    return x * y * z
"""
        assert result == expected

        # 複数のSTARTタグがある場合、最後のSTARTタグから最後までが対象
        diff_multiple = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 def process(data):
+    // MUTANT <START>
-    x = 1
+    x = 10
+    // MUTANT <END>
     y = 2
+    // MUTANT <START>
-    z = 3
-    return x + y + z
+    z = 30
+    return x * y * z
"""

        source_path = self.write_source(source)
        result_path = apply_diff_to_file_for_mutant(source_path, diff_multiple)
        
        assert result_path is not None
        result = result_path.read_text()
        expected_multiple = """def process(data):
    x = 10
    y = 2
    z = 30
    return x * y * z
"""
        assert result == expected_multiple 