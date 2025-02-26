#!/usr/bin/env python3
"""
可視化スクリプト: DIFFハンク、MUTANTハンク、DIFFの適用を可視化します。
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional
import colorama
from colorama import Fore, Style

# 必要なモジュールをインポート
from utils.detect_diff_hunks import DiffHunk, DiffHunkProcessor
from utils.mutant_diff_generator import MutantDiffGenerator, generate_mutant_diff, generate_mutant_diff_from_hunks
from utils.simple_diff_applier import apply_hunks, apply_hunk

# カラー出力の初期化
colorama.init()


def read_file(file_path: str) -> str:
    """ファイルを読み込みます。"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def visualize_hunk(hunk: DiffHunk, source_code: str) -> None:
    """ハンクを可視化します。"""
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}行番号範囲: {hunk.source_start_line} - {hunk.source_end_line}{Style.RESET_ALL}")
    
    # ハンクの内容を表示
    print(f"\n{Fore.CYAN}【ハンクの内容】{Style.RESET_ALL}")
    for line in hunk.diff_lines:
        if line.startswith('+'):
            print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
        elif line.startswith('-'):
            print(f"{Fore.RED}{line}{Style.RESET_ALL}")
        else:
            print(line)
    
    # 対応するソースコードの範囲を表示
    print(f"\n{Fore.CYAN}【対応するソースコード】{Style.RESET_ALL}")
    source_lines = source_code.split('\n')
    start_idx = max(0, hunk.source_start_line - 1)
    end_idx = min(len(source_lines), hunk.source_end_line)
    
    for i in range(start_idx, end_idx):
        line_num = i + 1
        print(f"{Fore.BLUE}{line_num:4d}:{Style.RESET_ALL} {source_lines[i]}")


def visualize_code_diff(original_code: str, modified_code: str, title: str = "コードの変更") -> None:
    """元のコードと変更後のコードの差分を可視化します。"""
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}【{title}】{Style.RESET_ALL}")
    
    original_lines = original_code.split('\n')
    modified_lines = modified_code.split('\n')
    
    # 行数の最大値を取得
    max_lines = max(len(original_lines), len(modified_lines))
    
    # 表示幅を調整
    column_width = 110
    
    print(f"{Fore.CYAN}{'元のコード':<{column_width}} | {'変更後のコード'}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'-'*column_width} | {'-'*column_width}{Style.RESET_ALL}")
    
    for i in range(max_lines):
        left = original_lines[i] if i < len(original_lines) else ""
        right = modified_lines[i] if i < len(modified_lines) else ""
        
        # 変更された行を色付けして表示
        if i < len(original_lines) and i < len(modified_lines) and original_lines[i] != modified_lines[i]:
            print(f"{Fore.RED}{left:<{column_width}}{Style.RESET_ALL} | {Fore.GREEN}{right}{Style.RESET_ALL}")
        else:
            print(f"{left:<{column_width}} | {right}")


def process_mutant_hunks(hunks: List[DiffHunk], source_code: str) -> List[DiffHunk]:
    """MUTANTハンクを処理して可視化します。"""
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}【MUTANTハンクの処理】{Style.RESET_ALL}")
    
    # MUTANTコメントを含むハンクを検出
    mutant_hunks = [i for i, hunk in enumerate(hunks, 1) 
                   if any("MUTANT" in line for line in hunk.diff_lines)]
    
    if not mutant_hunks:
        print(f"{Fore.YELLOW}MUTANTコメントを含むハンクはありません。{Style.RESET_ALL}")
        return hunks
    
    print(f"{Fore.YELLOW}MUTANTコメントを含むハンク: {', '.join(map(str, mutant_hunks))}{Style.RESET_ALL}")
    
    # MUTANTハンクを生成（ハンクオブジェクトを使用）
    generator = MutantDiffGenerator(hunks)
    result_hunks = generator.generate_hunks()
    
    print(f"{Fore.GREEN}生成されたMUTANTハンク数: {len(result_hunks)}{Style.RESET_ALL}")
    
    # 元のハンクとMUTANTハンクを比較
    for i, (orig_hunk, mutant_hunk) in enumerate(zip(hunks, result_hunks), 1):
        if any("MUTANT" in line for line in orig_hunk.diff_lines):
            print(f"\n{Fore.MAGENTA}【MUTANTハンク {i}】{Style.RESET_ALL}")
            print(f"{Fore.CYAN}元のハンク:{Style.RESET_ALL}")
            for line in orig_hunk.diff_lines:
                if "MUTANT" in line:
                    print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
                elif line.startswith('+'):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith('-'):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                else:
                    print(line)
            
            print(f"\n{Fore.CYAN}生成されたMUTANTハンク:{Style.RESET_ALL}")
            for line in mutant_hunk.diff_lines:
                if line.startswith('+'):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith('-'):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                else:
                    print(line)
    
    return result_hunks


def apply_diff_and_visualize(source_code: str, hunks: List[DiffHunk]) -> str:
    """DIFFを適用して結果を可視化します。"""
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}【DIFFの適用】{Style.RESET_ALL}")
    
    # DIFFを適用
    result_code = apply_hunks(source_code, hunks)
    
    # 変更前後のコードを可視化
    visualize_code_diff(source_code, result_code, "DIFFの適用結果")
    
    # 変更行数の集計
    original_lines = source_code.split('\n')
    result_lines = result_code.split('\n')
    added_lines = max(0, len(result_lines) - len(original_lines))
    removed_lines = max(0, len(original_lines) - len(result_lines))
    
    print(f"\n{Fore.GREEN}追加された行数: {added_lines}{Style.RESET_ALL}")
    print(f"{Fore.RED}削除された行数: {removed_lines}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}変更された合計行数: {added_lines + removed_lines}{Style.RESET_ALL}")
    
    return result_code


def parse_arguments():
    """コマンドライン引数を解析します。"""
    parser = argparse.ArgumentParser(description='DIFFハンク、MUTANTハンク、DIFFの適用を可視化します。')
    parser.add_argument('--source', '-s', help='ソースコードファイルのパス')
    parser.add_argument('--diff', '-d', help='DIFFファイルのパス')
    parser.add_argument('--mode', '-m', choices=['all', 'hunk', 'mutant', 'apply'], default='all',
                        help='実行モード (all: すべて, hunk: ハンクの可視化, mutant: MUTANTハンクの処理, apply: DIFFの適用)')
    parser.add_argument('--output', '-o', help='変更後のコードを保存するファイルパス')
    parser.add_argument('--save-mutant-diff', '-md', help='生成されたMUTANT DIFFを保存するファイルパス')
    return parser.parse_args()


def main():
    """メイン関数"""
    # コマンドライン引数の解析
    args = parse_arguments()
    
    # ファイルパスの設定
    source_path = args.source
    diff_path = args.diff
    
    # デフォルトのファイルパス
    if not source_path:
        source_path = "repositories/kotlin-tracer-mcp/src/main/kotlin/com/example/Finder.kt"
        # 環境に応じてパスを調整
        if not os.path.exists(source_path):
            source_path = input(f"{Fore.YELLOW}ソースコードファイルのパスを入力してください: {Style.RESET_ALL}")
    
    if not diff_path:
        diff_path = "debug/last_diff_generator.diff"
        # 環境に応じてパスを調整
        if not os.path.exists(diff_path):
            diff_path = input(f"{Fore.YELLOW}DIFFファイルのパスを入力してください: {Style.RESET_ALL}")
    
    # ファイルの読み込み
    try:
        source_code = read_file(source_path)
        diff_content = read_file(diff_path)
    except FileNotFoundError as e:
        print(f"{Fore.RED}エラー: ファイルが見つかりません - {e}{Style.RESET_ALL}")
        return 1
    
    # ハンクの抽出
    processor = DiffHunkProcessor(source_code, diff_content)
    hunks = processor.hunking()
    
    # 結果の表示
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}ソースファイル: {source_path}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}DIFFファイル: {diff_path}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}検出されたハンク数: {len(hunks)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    # 実行モードに応じて処理
    if args.mode in ['all', 'hunk']:
        # 各ハンクの可視化
        for i, hunk in enumerate(hunks, 1):
            print(f"\n{Fore.MAGENTA}【ハンク {i}/{len(hunks)}】{Style.RESET_ALL}")
            visualize_hunk(hunk, source_code)
    
    # MUTANTハンクの処理
    mutant_diff = None
    if args.mode in ['all', 'mutant']:
        mutant_hunks = process_mutant_hunks(hunks, source_code)
        
        # MUTANT DIFFを生成
        if any("MUTANT" in line for hunk in hunks for line in hunk.diff_lines):
            mutant_diff = generate_mutant_diff(source_code, diff_content)
            
            # MUTANT DIFFを保存
            if args.save_mutant_diff:
                try:
                    with open(args.save_mutant_diff, 'w', encoding='utf-8') as f:
                        f.write(mutant_diff)
                    print(f"{Fore.GREEN}MUTANT DIFFを {args.save_mutant_diff} に保存しました。{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}エラー: MUTANT DIFFの保存に失敗しました - {e}{Style.RESET_ALL}")
    else:
        mutant_hunks = hunks
    
    # DIFFの適用
    if args.mode in ['all', 'apply']:
        result_code = apply_diff_and_visualize(source_code, mutant_hunks)
        
        # 結果の保存
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result_code)
                print(f"{Fore.GREEN}変更後のコードを {args.output} に保存しました。{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}エラー: ファイルの保存に失敗しました - {e}{Style.RESET_ALL}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
