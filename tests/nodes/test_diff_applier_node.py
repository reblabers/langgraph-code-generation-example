import pytest
from nodes.diff_applier_node import DiffApplierNode
from utils.repository import Repository
from unittest.mock import Mock

class TestDiffApplierNode:
    @pytest.fixture
    def repository(self):
        return Mock(spec=Repository)

    @pytest.fixture
    def diff_applier_node(self, repository):
        return DiffApplierNode(repository)

    def test_extract_diff_mutants_single_mutant(self, diff_applier_node):
        """単一のMUTANTブロックを含むdiffのテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello():
MUTANT <START>
-    print("Hello")
+    print("Hello, World!")
MUTANT <END>
     return None"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 1
        assert result[0] == diff

    def test_extract_diff_mutants_multiple_mutants(self, diff_applier_node):
        """複数のMUTANTブロックを含むdiffのテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
+def hello_world():
MUTANT <END>
     print("Hello")
MUTANT <START>
-    return None
+    return "Hello"
MUTANT <END>"""

        expected1 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
+def hello_world():
MUTANT <END>
     print("Hello")
MUTANT <SKIP>
-    return None
+    return "Hello"
MUTANT <SKIP>"""

        expected2 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <SKIP>
-def hello():
+def hello_world():
MUTANT <SKIP>
     print("Hello")
MUTANT <START>
-    return None
+    return "Hello"
MUTANT <END>"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 2
        assert result[0] == expected1
        assert result[1] == expected2

    def test_extract_diff_mutants_no_mutants(self, diff_applier_node):
        """MUTANTブロックを含まないdiffのテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello():
     print("Hello")
     return None"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 0

    def test_extract_diff_mutants_unmatched_tags(self, diff_applier_node):
        """MUTANTの開始タグと終了タグの数が一致しない場合のテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
+def hello_world():
MUTANT <END>
MUTANT <START>
-    return None"""

        with pytest.raises(Exception) as exc_info:
            diff_applier_node._extract_diff_mutants(diff)
        assert "MUTANT <START>とMUTANT <END>の数が一致しません" in str(exc_info.value)

    def test_extract_diff_mutants_invalid_range(self, diff_applier_node):
        """開始位置が終了位置より後にある場合のテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <END>
-def hello():
+def hello_world():
MUTANT <START>"""

        with pytest.raises(Exception) as exc_info:
            diff_applier_node._extract_diff_mutants(diff)
        assert "MUTANTブロックの範囲が無効です" in str(exc_info.value)

    def test_extract_diff_mutants_empty_mutant(self, diff_applier_node):
        """空のMUTANTブロックを含むdiffのテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello():
MUTANT <START>
MUTANT <END>
     return None"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 1
        assert result[0] == diff

    def test_extract_diff_mutants_nested_mutants(self, diff_applier_node):
        """ネストされたMUTANTブロックを含むdiffのテスト（無効なケース）"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
MUTANT <START>
+def hello_world():
MUTANT <END>
MUTANT <END>"""

        with pytest.raises(Exception) as exc_info:
            diff_applier_node._extract_diff_mutants(diff)
        assert "ネストされたMUTANTブロックは許可されていません" in str(exc_info.value)

    def test_extract_diff_mutants_with_context(self, diff_applier_node):
        """コンテキスト行を含むdiffのテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
 # This is a context line
MUTANT <START>
-def old_function():
+def new_function():
MUTANT <END>
 # This is another context line"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 1
        assert result[0] == diff
        assert "# This is a context line" in result[0]
        assert "# This is another context line" in result[0] 
