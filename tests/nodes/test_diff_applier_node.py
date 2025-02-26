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
        """MUTANTの開始タグと終了タグの数が一致しない場合のテスト（許容ケース）"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
+def hello_world():
MUTANT <END>
MUTANT <START>
-    return None"""

        expected1 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
+def hello_world():
MUTANT <END>
MUTANT <SKIP>
-    return None"""

        expected2 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <SKIP>
-def hello():
+def hello_world():
MUTANT <SKIP>
MUTANT <START>
-    return None"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 2
        assert result[0] == expected1
        assert result[1] == expected2

    def test_extract_diff_mutants_invalid_range(self, diff_applier_node):
        """ENDタグが先に来る場合のテスト（許容ケース）"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <END>
-def hello():
+def hello_world():
MUTANT <START>"""

        expected = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <SKIP>
-def hello():
+def hello_world():
MUTANT <START>"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 1
        assert result[0] == expected

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
        """ネストされたMUTANTブロックを含むdiffのテスト（許容ケース）"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
MUTANT <START>
+def hello_world():
MUTANT <END>
MUTANT <END>"""

        expected1 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <START>
-def hello():
MUTANT <END>
+def hello_world():
MUTANT <SKIP>
MUTANT <SKIP>"""

        expected2 = """--- a/test.py
+++ b/test.py
@@ -1,5 +1,5 @@
MUTANT <SKIP>
-def hello():
MUTANT <START>
+def hello_world():
MUTANT <END>
MUTANT <SKIP>"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 2
        assert result[0] == expected1
        assert result[1] == expected2

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

    def test_extract_diff_mutants_missing_end_tag(self, diff_applier_node):
        """ENDタグがない場合、次のSTARTタグまでをMUTANTブロックとして扱うテスト"""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,7 +1,7 @@
MUTANT <START>
-def hello():
+def hello_world():
    print("Hello")
MUTANT <START>
-    return None
+    return "Hello"
MUTANT <END>"""

        expected1 = """--- a/test.py
+++ b/test.py
@@ -1,7 +1,7 @@
MUTANT <START>
-def hello():
+def hello_world():
    print("Hello")
MUTANT <END>
-    return None
+    return "Hello"
MUTANT <SKIP>"""

        expected2 = """--- a/test.py
+++ b/test.py
@@ -1,7 +1,7 @@
MUTANT <SKIP>
-def hello():
+def hello_world():
    print("Hello")
MUTANT <START>
-    return None
+    return "Hello"
MUTANT <END>"""

        result = diff_applier_node._extract_diff_mutants(diff)
        assert len(result) == 2
        assert result[0] == expected1
        assert result[1] == expected2 
