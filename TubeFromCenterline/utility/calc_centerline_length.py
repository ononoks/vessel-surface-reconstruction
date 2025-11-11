import csv
import math
import argparse
import sys

# GUI 用（引数が無いときに使う）
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None


def compute_cumulative_length(csv_file):
    """1本の中心線CSVから累積長さを計算する"""
    points = []
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            x = float(row['x'])
            y = float(row['y'])
            z = float(row['z'])
            points.append((x, y, z))

    if len(points) < 2:
        return 0.0

    cumulative_length = 0.0
    for i in range(1, len(points)):
        x1, y1, z1 = points[i - 1]
        x2, y2, z2 = points[i]
        distance = math.sqrt(
            (x2 - x1)**2 +
            (y2 - y1)**2 +
            (z2 - z1)**2
        )
        cumulative_length += distance

    return cumulative_length


def process_files(file_list):
    """複数ファイルをまとめて処理（バッチ処理用の入り口）"""
    results = {}
    for path in file_list:
        try:
            length = compute_cumulative_length(path)
            results[path] = length
            print(f"{path}: 累積長さ = {length:.6f}")
        except Exception as e:
            print(f"{path}: エラーが発生しました: {e}", file=sys.stderr)
    return results


def select_files_via_gui():
    """GUIでファイルを選択（複数選択可）"""
    if tk is None or filedialog is None:
        print("tkinter が利用できないため、GUIでの選択は使えません。", file=sys.stderr)
        return []

    root = tk.Tk()
    root.withdraw()  # メインウィンドウを表示しない

    file_paths = filedialog.askopenfilenames(
        title="中心線CSVファイルを選択",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    # askopenfilenames はタプルを返すのでリストに変換
    return list(file_paths)


def main():
    parser = argparse.ArgumentParser(
        description="中心線CSVの累積長さを計算するスクリプト"
    )
    # 複数ファイルを指定できるようにしておく（バッチ処理向け）
    parser.add_argument(
        "files",
        nargs="*",
        help="入力CSVファイル（複数指定可）。指定がなければGUIで選択。"
    )

    args = parser.parse_args()

    if args.files:
        # コマンドラインから指定されたファイルを処理
        process_files(args.files)
    else:
        # 引数が無い場合はGUIで選択
        file_list = select_files_via_gui()
        if not file_list:
            print("ファイルが選択されませんでした。処理を終了します。")
            sys.exit(0)
        process_files(file_list)


if __name__ == "__main__":
    main()
