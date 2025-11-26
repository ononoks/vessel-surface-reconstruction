import csv
import math
import argparse
import sys
import os
import glob
import statistics  # 追加: 統計量計算用

# グラフ描画用
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# GUI 用（引数が無いときに使う）
try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None


def compute_cumulative_length(csv_file):
    # 1本の中心線CSVから累積長さを計算する
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


def select_directory_via_gui():
    # GUIでディレクトリを選択
    if tk is None or filedialog is None:
        print("tkinter が利用できないため、GUIでの選択は使えません。", file=sys.stderr)
        return None

    root = tk.Tk()
    root.withdraw()  # メインウィンドウを表示しない

    dir_path = filedialog.askdirectory(
        title="中心線CSVファイルがあるディレクトリを選択"
    )

    if not dir_path:
        return None

    return dir_path


def plot_histogram(lengths, output_png):
    """
    total_length の度数分布を棒グラフ（ヒストグラム）として png で保存
    横軸: total_length, 縦軸: 度数（ファイル数）
    """
    if plt is None:
        print("matplotlib がインポートできないため、グラフは出力されません。", file=sys.stderr)
        return

    if not lengths:
        print("ヒストグラムを作成するデータがありません。", file=sys.stderr)
        return

    # ヒストグラム作成
    plt.figure()
    plt.hist(lengths, bins='auto')   # 自動でビン数を決める
    plt.xlabel("total_length")
    plt.ylabel("frequency (number of files)")
    plt.title("Histogram of total_length")
    plt.tight_layout()
    plt.savefig(output_png)
    plt.close()

    print(f"ヒストグラムを {output_png} に保存しました。")


def output_calc_result(lengths, output_csv):
    """
    total_length の最小値・最大値・中央値・平均値を計算し、
    output_csv と同じディレクトリに calc_rusult.txt として出力する。
    """
    if not lengths:
        print("calc_rusult.txt を作成するためのデータがありません。", file=sys.stderr)
        return

    min_len = min(lengths)
    max_len = max(lengths)
    median_len = statistics.median(lengths)
    mean_len = statistics.mean(lengths)

    # output_csv と同じディレクトリに出力
    out_dir = os.path.dirname(os.path.abspath(output_csv))
    calc_result_path = os.path.join(out_dir, "calc_rusult.txt")

    with open(calc_result_path, "w", encoding="utf-8") as f:
        f.write("total_length の統計量\n")
        f.write(f"ファイル数: {len(lengths)}\n")
        f.write(f"最小値 (min): {min_len:.6f}\n")
        f.write(f"最大値 (max): {max_len:.6f}\n")
        f.write(f"中央値 (median): {median_len:.6f}\n")
        f.write(f"平均値 (mean): {mean_len:.6f}\n")

    print(f"統計量を {calc_result_path} に書き出しました。")


def process_directory(input_dir, output_csv):
    """
    指定ディレクトリ内の *.csv をすべて処理し、
    filename, total_length をまとめた output_csv を出力し、
    さらに total_length の度数分布を png で出力し、
    total_length の最小値・最大値・中央値・平均値を calc_rusult.txt に出力する。
    """
    # ディレクトリ内の *.csv ファイル一覧
    pattern = os.path.join(input_dir, "*.csv")
    csv_files = sorted(glob.glob(pattern))

    # 自分がこれから書く出力ファイルを一覧から除外（念のため）
    csv_files = [f for f in csv_files if os.path.abspath(f) != os.path.abspath(output_csv)]

    if not csv_files:
        print("指定ディレクトリ内に *.csv ファイルが見つかりませんでした。")
        return

    results = []

    for path in csv_files:
        try:
            length = compute_cumulative_length(path)
            filename_only = os.path.basename(path)
            results.append((filename_only, length))
            print(f"{filename_only}: total length = {length:.6f}")
        except Exception as e:
            print(f"{path}: エラーが発生しました: {e}", file=sys.stderr)

    # 結果をまとめてCSVに書き出し
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "total_length"])
        for filename, length in results:
            writer.writerow([filename, f"{length:.6f}"])

    print(f"\n結果を {output_csv} に書き出しました。")

    # total_length の配列を作ってヒストグラムを出力
    lengths = [length for _, length in results]
    # 出力PNGファイル名（output_csv と同じ場所・同じベース名に "_hist.png" を付ける）
    base, _ = os.path.splitext(output_csv)
    output_png = base + "_hist.png"
    plot_histogram(lengths, output_png)

    # 追加: 統計量を calc_rusult.txt に出力
    output_calc_result(lengths, output_csv)


def main():
    parser = argparse.ArgumentParser(
        description="ディレクトリ内の中心線CSVの累積長さを一括計算し、結果CSVとヒストグラムPNGおよび統計量テキストを出力するスクリプト"
    )
    parser.add_argument(
        "-d", "--dir",
        help="入力CSVファイルがあるディレクトリ。省略時はGUIで選択。"
    )
    parser.add_argument(
        "-o", "--output",
        help="出力CSVファイル名（パス）。省略時は '<dir>/centerline_lengths.csv'。"
    )

    args = parser.parse_args()

    # ディレクトリを決定
    if args.dir:
        input_dir = args.dir
    else:
        input_dir = select_directory_via_gui()
        if not input_dir:
            print("ディレクトリが選択されませんでした。処理を終了します。")
            sys.exit(0)

    # 出力ファイルパスを決定
    if args.output:
        output_csv = args.output
    else:
        output_csv = os.path.join(input_dir, "centerline_lengths.csv")

    process_directory(input_dir, output_csv)


if __name__ == "__main__":
    main()
