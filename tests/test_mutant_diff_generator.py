import unittest
from typing import List

from utils.detect_diff_hunks import DiffHunk
from utils.mutant_diff_generator import (
    MutantDiffGenerator,
    generate_mutant_diff,
    generate_mutant_diff_from_hunks
)


class TestMutantDiffGenerator(unittest.TestCase):
    """MutantDiffGeneratorのテストクラス"""
    
    def test_init(self):
        """初期化のテスト"""
        hunks = [
            DiffHunk([" line1", " line2"], 1, 2),
            DiffHunk([" line3", " line4"], 3, 4)
        ]
        generator = MutantDiffGenerator(hunks)
        
        self.assertEqual(generator.hunks, hunks)
        self.assertIsNotNone(generator.mutant_start_pattern)
        self.assertIsNotNone(generator.mutant_end_pattern)
    
    def test_process_hunk_with_mutant_state_no_mutant(self):
        """MUTANT状態がない場合のハンク処理テスト"""
        hunks = [
            DiffHunk(["@@ -1,3 +1,3 @@", " line1", "-line2", "+new line2", " line3"], 1, 3)
        ]
        generator = MutantDiffGenerator(hunks)
        
        processed_hunk, is_mutating = generator._process_hunk_with_mutant_state(hunks[0], False)
        
        # 削除行が優先され、追加行は無視される
        self.assertEqual(processed_hunk.diff_lines, ["@@ -1,3 +1,3 @@", " line1", " line2", " line3"])
        self.assertFalse(is_mutating)  # MUTANT状態は変わらない
    
    def test_process_hunk_with_mutant_state_with_mutant(self):
        """MUTANT状態がある場合のハンク処理テスト"""
        hunks = [
            DiffHunk(["@@ -1,3 +1,3 @@", " line1", "-line2", "+new line2", " line3"], 1, 3)
        ]
        generator = MutantDiffGenerator(hunks)
        
        processed_hunk, is_mutating = generator._process_hunk_with_mutant_state(hunks[0], True)
        
        # MUTANT状態では追加行と削除行が保持される
        self.assertEqual(processed_hunk.diff_lines, ["@@ -1,3 +1,3 @@", " line1", "-line2", "+new line2", " line3"])
        self.assertTrue(is_mutating)  # MUTANT状態は維持される
    
    def test_process_hunk_with_mutant_tags(self):
        """MUTANTタグを含むハンク処理テスト"""
        hunks = [
            DiffHunk([
                "@@ -1,5 +1,5 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                "+// MUTANT <END>", 
                " line3"
            ], 1, 5)
        ]
        generator = MutantDiffGenerator(hunks)
        
        processed_hunk, is_mutating = generator._process_hunk_with_mutant_state(hunks[0], False)
        
        # MUTANTタグは除外され、タグ内の追加行が優先される
        self.assertEqual(processed_hunk.diff_lines, ["@@ -1,5 +1,5 @@", " line1", " line2", "+new line2", " line3"])
        self.assertFalse(is_mutating)  # 最終的にMUTANT状態は終了している
    
    def test_generate_hunks_no_mutant_tags(self):
        """MUTANTタグがない場合のハンク生成テスト"""
        hunks = [
            DiffHunk(["@@ -1,3 +1,3 @@", " line1", "-line2", "+new line2", " line3"], 1, 3)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # MUTANTタグがない場合は元のハンクがそのまま返される
        self.assertEqual(result, hunks)
    
    def test_generate_hunks_with_mutant_tags(self):
        """MUTANTタグがある場合のハンク生成テスト"""
        hunks = [
            DiffHunk([
                "@@ -1,5 +1,5 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                "+// MUTANT <END>", 
                " line3"
            ], 1, 5)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # MUTANTタグは除外され、タグ内の追加行が優先される
        self.assertEqual(result[0].diff_lines, ["@@ -1,5 +1,5 @@", " line1", " line2", "+new line2", " line3"])
    
    def test_generate_hunks_with_multiple_mutant_sections(self):
        """複数のMUTANTセクションがある場合のハンク生成テスト"""
        hunks = [
            DiffHunk([
                "@@ -1,7 +1,7 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                "+// MUTANT <END>", 
                " line3",
                "-line4",
                "+// MUTANT <START>",
                "+new line4",
                "+// MUTANT <END>",
                " line5"
            ], 1, 7)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # 両方のMUTANTセクション内の追加行が優先される
        self.assertEqual(result[0].diff_lines, [
            "@@ -1,7 +1,7 @@", 
            " line1", 
            " line2", 
            "+new line2", 
            " line3",
            " line4",
            "+new line4",
            " line5"
        ])
    
    def test_generate_hunks_with_unclosed_mutant(self):
        """閉じられていないMUTANTタグがある場合のハンク生成テスト"""
        hunks = [
            DiffHunk([
                "@@ -1,5 +1,5 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                " line3"
            ], 1, 5)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # 閉じられていないMUTANTセクション内の追加行が保持され、削除行は空白行に変換される
        expected_lines = ["@@ -1,5 +1,5 @@", " line1", " line2", "+new line2", " line3"]
        self.assertEqual(result[0].diff_lines, expected_lines)
    
    def test_generate_hunks_with_multiple_hunks(self):
        """複数のハンクがある場合のハンク生成テスト"""
        hunks = [
            DiffHunk([
                "@@ -1,3 +1,3 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                "+// MUTANT <END>", 
                " line3"
            ], 1, 3),
            DiffHunk([
                "@@ -5,3 +5,3 @@", 
                " line5", 
                "-line6", 
                "+new line6", 
                " line7"
            ], 5, 7)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # 最初のハンクはMUTANTタグ内の追加行が優先される
        self.assertEqual(result[0].diff_lines, ["@@ -1,3 +1,3 @@", " line1", " line2", "+new line2", " line3"])
        # 2番目のハンクは削除行が優先される（MUTANTタグなし）
        self.assertEqual(result[1].diff_lines, ["@@ -5,3 +5,3 @@", " line5", " line6", " line7"])
    
    def test_generate_hunks_with_mutant_state_across_hunks(self):
        """ハンクをまたがるMUTANT状態のテスト"""
        hunks = [
            DiffHunk([
                "@@ -1,3 +1,3 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                " line3"
            ], 1, 3),
            DiffHunk([
                "@@ -5,3 +5,3 @@", 
                " line5", 
                "-line6", 
                "+new line6", 
                "+// MUTANT <END>", 
                " line7"
            ], 5, 7)
        ]
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        # 最初のハンクはMUTANTタグ内の追加行が保持され、削除行は空白行に変換される
        expected_lines1 = ["@@ -1,3 +1,3 @@", " line1", " line2", "+new line2", " line3"]
        self.assertEqual(result[0].diff_lines, expected_lines1)
        
        # 2番目のハンクはMUTANT状態が引き継がれているため、追加行と削除行が保持される
        expected_lines2 = ["@@ -5,3 +5,3 @@", " line5", "-line6", "+new line6", " line7"]
        self.assertEqual(result[1].diff_lines, expected_lines2)
    
    def test_generate_mutant_diff(self):
        """generate_mutant_diff関数のテスト"""
        code = """line1
line2
line3
line4
line5"""
        
        diff = """@@ -1,5 +1,5 @@
 line1
-line2
+// MUTANT <START>
+new line2
+// MUTANT <END>
 line3
-line4
+new line4
 line5"""
        
        result = generate_mutant_diff(code, diff)
        
        # 実際の出力を厳密に検証
        expected_result = " line1\n line2\n+new line2\n line3\n line4\n line5"
        self.assertEqual(result, expected_result)
    
    def test_generate_mutant_diff_from_hunks(self):
        """generate_mutant_diff_from_hunks関数のテスト"""
        hunks = [
            DiffHunk([
                "@@ -1,3 +1,3 @@", 
                " line1", 
                "-line2", 
                "+// MUTANT <START>", 
                "+new line2", 
                "+// MUTANT <END>", 
                " line3"
            ], 1, 3)
        ]
        
        result = generate_mutant_diff_from_hunks(hunks)
        
        self.assertEqual(result[0].diff_lines, ["@@ -1,3 +1,3 @@", " line1", " line2", "+new line2", " line3"])
    
    def test_empty_diff(self):
        """空のDIFFのテスト"""
        code = "line1\nline2\nline3"
        diff = ""
        
        result = generate_mutant_diff(code, diff)
        
        self.assertEqual(result, "")
    
    def test_no_hunks(self):
        """ハンクがない場合のテスト"""
        hunks = []
        generator = MutantDiffGenerator(hunks)
        
        result = generator.generate_hunks()
        
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
