import unittest
from utils.adjust_diff_context import DiffContextAdjuster, adjust_diff_context
from utils.detect_diff_hunks import DiffHunk, DiffHunkProcessor


class TestDiffContextAdjuster(unittest.TestCase):
    """DiffContextAdjusterのテストクラス"""
    
    def test_adjust_hunk_with_matching_context(self):
        """一致するコンテキスト行を持つハンクのテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
    return True
"""
        # テスト用のDiffHunk
        diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return True"
        ]
        hunk = DiffHunk(diff_lines, 1, 3)
        
        # DiffContextAdjusterを作成
        adjuster = DiffContextAdjuster(source_code)
        
        # ハンクを調整
        adjusted_hunk = adjuster.adjust_hunk(hunk)
        
        # 調整後のdiff_linesを確認
        expected_diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return True"
        ]
        self.assertEqual(adjusted_hunk.diff_lines, expected_diff_lines)
    
    def test_adjust_hunk_with_non_matching_context(self):
        """一致しないコンテキスト行を持つハンクのテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
    return True
"""
        # テスト用のDiffHunk（一致しないコンテキスト行を含む）
        diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return False"  # ソースコードと一致しない
        ]
        hunk = DiffHunk(diff_lines, 1, 3)
        
        # DiffContextAdjusterを作成
        adjuster = DiffContextAdjuster(source_code)
        
        # ハンクを調整
        adjusted_hunk = adjuster.adjust_hunk(hunk)
        
        # 調整後のdiff_linesを確認
        expected_diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            "+return False"  # '+'に変換される
        ]
        self.assertEqual(adjusted_hunk.diff_lines, expected_diff_lines)
    
    def test_adjust_hunk_with_out_of_range_context(self):
        """範囲外のコンテキスト行を持つハンクのテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
"""
        # テスト用のDiffHunk（範囲外のコンテキスト行を含む）
        diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return True"  # ソースコードに存在しない
        ]
        hunk = DiffHunk(diff_lines, 1, 2)
        
        # DiffContextAdjusterを作成
        adjuster = DiffContextAdjuster(source_code)
        
        # ハンクを調整
        adjusted_hunk = adjuster.adjust_hunk(hunk)
        
        # 調整後のdiff_linesを確認
        expected_diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            "+return True"  # '+'に変換される
        ]
        self.assertEqual(adjusted_hunk.diff_lines, expected_diff_lines)
    
    def test_adjust_diff_context(self):
        """adjust_diff_context関数のテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
    return True
"""
        # テスト用のDIFF
        diff = """--- a/example.py
+++ b/example.py
@@ -1,3 +1,3 @@
 def example():
-    print("Hello")
+    print("Hello, World!")
 return False
"""
        
        # DIFFを調整
        adjusted_diff = adjust_diff_context(source_code, diff)
        
        # 調整後のDIFFを確認
        expected_diff = """--- a/example.py
+++ b/example.py
@@ -1,3 +1,3 @@
 def example():
-    print("Hello")
+    print("Hello, World!")
+return False
"""
        self.assertEqual(adjusted_diff, expected_diff)

    def test_adjust_hunk_with_similar_context(self):
        """類似するが完全一致ではないコンテキスト行を持つハンクのテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
    return True
"""
        # テスト用のDiffHunk（類似するが完全一致ではないコンテキスト行を含む）
        diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return True  # 終了"  # ソースコードと類似するが完全一致ではない
        ]
        hunk = DiffHunk(diff_lines, 1, 3)
        
        # DiffContextAdjusterを作成
        adjuster = DiffContextAdjuster(source_code)
        
        # ハンクを調整
        adjusted_hunk = adjuster.adjust_hunk(hunk)
        
        # 調整後のdiff_linesを確認
        # 類似度が高いため、コンテキスト行として扱われるはず
        expected_diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return True  # 終了"
        ]
        self.assertEqual(adjusted_hunk.diff_lines, expected_diff_lines)
    
    def test_adjust_hunk_with_low_similarity_context(self):
        """類似度が低いコンテキスト行を持つハンクのテスト"""
        # テスト用のソースコード
        source_code = """def example():
    print("Hello")
    return True
"""
        # テスト用のDiffHunk（類似度が低いコンテキスト行を含む）
        diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            " return False  # 全く異なるコメント"  # 類似度が低い
        ]
        hunk = DiffHunk(diff_lines, 1, 3)
        
        # DiffContextAdjusterを作成
        adjuster = DiffContextAdjuster(source_code)
        
        # ハンクを調整
        adjusted_hunk = adjuster.adjust_hunk(hunk)
        
        # 調整後のdiff_linesを確認
        # 類似度が低いため、追加行として扱われるはず
        expected_diff_lines = [
            " def example():",
            "-    print(\"Hello\")",
            "+    print(\"Hello, World!\")",
            "+return False  # 全く異なるコメント"
        ]
        self.assertEqual(adjusted_hunk.diff_lines, expected_diff_lines)


if __name__ == "__main__":
    unittest.main() 