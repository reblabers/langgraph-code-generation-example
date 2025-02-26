import unittest
from utils.detect_diff_hunks import DiffHunk
from utils.simple_diff_applier import apply_hunk, apply_hunks, _is_content_similar, _calculate_line_changes
from pathlib import Path
import tempfile
import os


class TestSimpleDiffApplier(unittest.TestCase):
    
    def test_apply_hunk_add_line(self):
        """行追加のテスト"""
        source_code = "line1\nline2\nline3"
        hunk_lines = [" line1", "+new line", " line2", " line3"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "line1\nnew line\nline2\nline3"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunk_remove_line(self):
        """行削除のテスト"""
        source_code = "line1\nline2\nline3"
        hunk_lines = [" line1", "-line2", " line3"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "line1\nline3"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunk_replace_line(self):
        """行置換のテスト"""
        source_code = "line1\nline2\nline3"
        hunk_lines = [" line1", "-line2", "+new line2", " line3"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "line1\nnew line2\nline3"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunk_multiple_changes(self):
        """複数行の変更テスト"""
        source_code = "line1\nline2\nline3\nline4\nline5"
        hunk_lines = [" line1", "+new line1.5", " line2", "-line3", "+new line3", " line4", " line5"]
        hunk = DiffHunk(hunk_lines, 1, 5)
        
        result = apply_hunk(source_code, hunk)
        expected = "line1\nnew line1.5\nline2\nnew line3\nline4\nline5"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunk_with_whitespace_differences(self):
        """空白の違いを無視するテスト"""
        source_code = "line1\n  line2  \nline3"
        hunk_lines = [" line1", "- line2 ", "+  new line2  ", " line3"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "line1\n  new line2  \nline3"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunks(self):
        """複数のハンクを適用するテスト"""
        source_code = "line1\nline2\nline3\nline4\nline5"
        
        # 最初のハンク: line2の後に新しい行を追加
        hunk1_lines = [" line1", " line2", "+new line2.5", " line3"]
        hunk1 = DiffHunk(hunk1_lines, 1, 3)
        
        # 2番目のハンク: line4を置換
        hunk2_lines = [" line3", " line4", "-line5", "+new line5"]
        hunk2 = DiffHunk(hunk2_lines, 3, 5)
        
        result = apply_hunks(source_code, [hunk1, hunk2])
        expected = "line1\nline2\nnew line2.5\nline3\nline4\nnew line5"
        
        self.assertEqual(result, expected)
    
    def test_apply_hunk_out_of_range(self):
        """範囲外の行番号を指定した場合のテスト"""
        source_code = "line1\nline2\nline3"
        hunk_lines = [" line1", " line2", " line3", " line4"]
        hunk = DiffHunk(hunk_lines, 1, 4)  # 4行目は存在しない
        
        with self.assertRaises(ValueError):
            apply_hunk(source_code, hunk)

    def test_is_content_similar(self):
        """_is_content_similarの動作確認テスト"""
        # 空白の違いを無視するケース
        self.assertTrue(_is_content_similar("test", "test"))
        self.assertTrue(_is_content_similar("  test  ", "test"))
        self.assertTrue(_is_content_similar("test", "  test  "))
        self.assertTrue(_is_content_similar("  test  ", "  test  "))
        
        # 空白以外の違いがあるケース
        self.assertFalse(_is_content_similar("test", "test2"))
        self.assertFalse(_is_content_similar("test", "tset"))
        
        # 特殊なケース
        self.assertTrue(_is_content_similar("", ""))
        self.assertTrue(_is_content_similar("  ", ""))
        self.assertTrue(_is_content_similar("", "  "))

    def test_calculate_line_changes(self):
        """_calculate_line_changesの動作確認テスト"""
        # 行が追加されるケース
        added, deleted = _calculate_line_changes("line1\nline2", "line1\nline2\nline3")
        self.assertEqual(added, 1)
        self.assertEqual(deleted, 0)
        
        # 行が削除されるケース
        added, deleted = _calculate_line_changes("line1\nline2\nline3", "line1\nline2")
        self.assertEqual(added, 0)
        self.assertEqual(deleted, 1)
        
        # 行数が変わらないケース
        added, deleted = _calculate_line_changes("line1\nline2", "line1\nline2_modified")
        self.assertEqual(added, 0)
        self.assertEqual(deleted, 0)
        
        # 複数行の追加と削除
        added, deleted = _calculate_line_changes("line1\nline2\nline3", "line1\nline2\nline3\nline4\nline5")
        self.assertEqual(added, 2)
        self.assertEqual(deleted, 0)
        
        # 空のケース
        added, deleted = _calculate_line_changes("", "")
        self.assertEqual(added, 0)
        self.assertEqual(deleted, 0)

    def test_whitespace_only_diff(self):
        """空白行のみのdiffが正しく処理されることを確認するテスト"""
        source_code = "def hello():\n    print(\"Hello\")\n    print(\"World\")\n"
        hunk_lines = [" def hello():", "     print(\"Hello\")", "+", "     print(\"World\")"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "def hello():\n    print(\"Hello\")\n\n    print(\"World\")\n"
        
        self.assertEqual(result, expected)

    def test_multiple_consecutive_whitespace_diff(self):
        """複数の連続した空白行を含むdiffが正しく処理されることを確認するテスト"""
        source_code = "def hello():\n    print(\"Hello\")\n    print(\"World\")\n"
        hunk_lines = [" def hello():", "     print(\"Hello\")", "+", "+", "     print(\"World\")"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "def hello():\n    print(\"Hello\")\n\n\n    print(\"World\")\n"
        
        self.assertEqual(result, expected)

    def test_non_ascii_diff(self):
        """非ASCII文字（日本語など）を含むdiffが正しく処理されることを確認するテスト"""
        source_code = "def hello():\n    print(\"Hello\")\n    # コメント\n    print(\"World\")\n"
        hunk_lines = [" def hello():", "     print(\"Hello\")", "-    # コメント", "+    # 日本語コメント", "     print(\"World\")"]
        hunk = DiffHunk(hunk_lines, 1, 4)
        
        result = apply_hunk(source_code, hunk)
        expected = "def hello():\n    print(\"Hello\")\n    # 日本語コメント\n    print(\"World\")\n"
        
        self.assertEqual(result, expected)

    def test_no_newline_at_eof(self):
        """ファイルの最後に改行がない場合の処理を確認"""
        source_code = "def hello():\n    print(\"Hello\")\n    print(\"World\")"  # 最後に改行なし
        hunk_lines = [" def hello():", "     print(\"Hello\")", "-    print(\"World\")", "+    print(\"Goodbye\")"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "def hello():\n    print(\"Hello\")\n    print(\"Goodbye\")"
        
        self.assertEqual(result, expected)

    def test_non_matching_context_line(self):
        """信頼できる状態で、ソースコードに存在しない無印行（コンテキスト行）が
        正しく処理されることを確認するテスト"""
        source_code = "def hello():\n    print(\"Hello\")\n    print(\"World\")\n"
        # 最初の行で一致を確立し、その後に存在しない行を含むdiff
        hunk_lines = [" def hello():", "     print(\"Different line\")", "+    print(\"Extra line\")", "-    print(\"Hello\")", "     print(\"World\")"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        # simple_diff_applierの実装では、コンテキスト行が一致しない場合は元のソースコードの行を使用する
        # また、削除行が一致しない場合も元のソースコードの行を使用する
        expected = "def hello():\n    print(\"Hello\")\n    print(\"Extra line\")\n"
        
        self.assertEqual(result, expected)

    def test_content_equal_with_whitespace_diff(self):
        """空白の違いがあるdiffが正しく適用されることを確認するテスト"""
        # 元のコード（インデントが異なる）
        source_code = "def calculate(x, y):\n    result = x + y\n    return result\n"
        # DIFFの内容（空白の違いがある）
        hunk_lines = [" def calculate(x, y):", "-    result = x + y", "+    result=x+y", "-    return result", "+    return  result"]
        hunk = DiffHunk(hunk_lines, 1, 3)
        
        result = apply_hunk(source_code, hunk)
        expected = "def calculate(x, y):\n    result=x+y\n    return  result\n"
        
        self.assertEqual(result, expected)

    def test_reliable_match_with_similar_lines(self):
        """類似した行が複数ある場合に信頼できるマッチングが機能することを確認するテスト"""
        # 元のコード（類似した行が複数ある）
        source_code = "def process_data():\n    data = get_data()\n    # 処理開始\n    process_item(data, 1)\n    process_item(data, 2)\n    process_item(data, 3)\n    process_item(data, 4)\n    process_item(data, 5)\n    # 処理終了\n    return data\n"
        # DIFFの内容（類似した行の間に新しい行を追加）
        hunk_lines = [
            " def process_data():",
            "     data = get_data()",
            "     # 処理開始",
            "-    process_item(data, 1)",
            "+    log(\"処理を開始します\")",
            "     process_item(data, 2)",
            "     process_item(data, 3)",
            "+    process_item(data, 3.5)  # 追加の処理",
            "     process_item(data, 4)",
            "-    process_item(data, 5)",
            "+    process_item(data, 5.0)",
            "     # 処理終了",
            "     return data"
        ]
        hunk = DiffHunk(hunk_lines, 1, 10)
        
        result = apply_hunk(source_code, hunk)
        expected = "def process_data():\n    data = get_data()\n    # 処理開始\n    log(\"処理を開始します\")\n    process_item(data, 2)\n    process_item(data, 3)\n    process_item(data, 3.5)  # 追加の処理\n    process_item(data, 4)\n    process_item(data, 5.0)\n    # 処理終了\n    return data\n"
        
        self.assertEqual(result, expected)

    def test_apply_hunks_with_line_offset(self):
        """行オフセットが正しく計算されるかテスト"""
        source_code = "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10"
        
        # 最初のハンク: line2の後に2行追加
        hunk1_lines = [" line1", " line2", "+new line2.1", "+new line2.2", " line3"]
        hunk1 = DiffHunk(hunk1_lines, 1, 3)
        
        # 2番目のハンク: line5を削除
        hunk2_lines = [" line4", "-line5", " line6"]
        hunk2 = DiffHunk(hunk2_lines, 4, 6)
        
        # 3番目のハンク: line8を置換
        hunk3_lines = [" line7", "-line8", "+new line8", " line9"]
        hunk3 = DiffHunk(hunk3_lines, 7, 9)
        
        result = apply_hunks(source_code, [hunk1, hunk2, hunk3])
        expected = "line1\nline2\nnew line2.1\nnew line2.2\nline3\nline4\nline6\nline7\nnew line8\nline9\nline10"
        
        self.assertEqual(result, expected)

    def test_edge_cases_with_content_equal(self):
        """_is_content_similarの境界ケースを実際のdiffで確認するテスト"""
        # 元のコード（特殊な空白文字やコメントを含む）
        source_code = """def special_cases():
    # タブとスペースの混在
	x = 1  # タブでインデント
    y = 2  # スペースでインデント
    
    # 特殊な空白文字
    z = x +　y  # 全角スペース
    
    # コメント内の空白
    # これは    コメントです
    
    return z
"""
        # DIFFの内容（空白の扱いが重要なケース）
        hunk_lines = [
            " def special_cases():",
            "     # タブとスペースの混在",
            "-	x = 1  # タブでインデント",
            "+    x = 100  # スペースでインデント",
            "     y = 2  # スペースでインデント",
            "     ",
            "     # 特殊な空白文字",
            "-    z = x +　y  # 全角スペース",
            "+    z = x + y  # 半角スペース",
            "     ",
            "     # コメント内の空白",
            "-    # これは    コメントです",
            "+    # これは コメントです",
            "     ",
            "     return z"
        ]
        hunk = DiffHunk(hunk_lines, 1, 11)
        
        result = apply_hunk(source_code, hunk)
        expected = """def special_cases():
    # タブとスペースの混在
    x = 100  # スペースでインデント
    y = 2  # スペースでインデント
    
    # 特殊な空白文字
    z = x + y  # 半角スペース
    
    # コメント内の空白
    # これは コメントです
    
    return z
"""
        self.assertEqual(result, expected)

    def test_large_diff_performance(self):
        """大きなdiffファイルの処理（パフォーマンステスト）"""
        # 大きなソースファイルを生成
        source_lines = ["def test_function():\n"]
        for i in range(100):  # 1000から100に減らして高速化
            source_lines.append(f"    print('Line {i}')\n")
        source = "".join(source_lines)
        
        # 大きなdiffを生成（10行を変更）
        diff_lines = []
        diff_lines.append(" def test_function():")
        for i in range(100):
            if i % 10 == 0:  # 10行ごとに1行を変更
                diff_lines.append(f"-    print('Line {i}')")
                diff_lines.append(f"+    print('Modified Line {i}')")
            else:
                diff_lines.append(f"     print('Line {i}')")
        
        hunk = DiffHunk(diff_lines, 1, 101)
        
        result = apply_hunk(source, hunk)
        
        # 変更が正しく適用されていることを確認
        result_lines = result.splitlines()
        for i in range(100):
            if i % 10 == 0:
                self.assertIn(f"    print('Modified Line {i}')", result_lines)
            else:
                self.assertIn(f"    print('Line {i}')", result_lines)

    def test_mutant_like_changes(self):
        """MUTANTタグのような特殊なコメントを含む変更のテスト"""
        source_code = """def calculate(x, y):
    return x + y
"""
        hunk_lines = [
            " def calculate(x, y):",
            "+    // MUTANT <START>",
            "-    return x + y",
            "+    return x - y",
            "+    // MUTANT <END>"
        ]
        hunk = DiffHunk(hunk_lines, 1, 2)
        
        result = apply_hunk(source_code, hunk)
        expected = """def calculate(x, y):
    // MUTANT <START>
    return x - y
    // MUTANT <END>
"""
        self.assertEqual(result, expected)

    def test_incomplete_diff(self):
        """不完全なdiffが正しく処理されることを確認するテスト"""
        source_code = "line1\nline2\nline3\nline4\nline5"
        
        # 削除行のみのdiff
        hunk1_lines = [" line1", "-line2", " line3"]
        hunk1 = DiffHunk(hunk1_lines, 1, 3)
        
        result1 = apply_hunk(source_code, hunk1)
        expected1 = "line1\nline3\nline4\nline5"
        self.assertEqual(result1, expected1)
        
        # 追加行のみのdiff
        hunk2_lines = [" line1", "+new line", " line2"]
        hunk2 = DiffHunk(hunk2_lines, 1, 2)
        
        result2 = apply_hunk(source_code, hunk2)
        expected2 = "line1\nnew line\nline2\nline3\nline4\nline5"
        self.assertEqual(result2, expected2)


if __name__ == "__main__":
    unittest.main() 