import os
import numpy as np
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog

def read_ply_vertex_data(path):
    """
    ASCII PLY から vertex 部分だけ読み込み、
    x, y, z, curvature を numpy 配列で返す。
    （ヘッダの property 行を見て列位置を自動で判定）
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    num_vertices = None
    in_vertex_element = False
    vertex_properties = []
    header_end_idx = None

    # ---- ヘッダの解析 ----
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('element vertex'):
            # 例: "element vertex 300"
            parts = line.split()
            num_vertices = int(parts[2])
            in_vertex_element = True

        elif line.startswith('element') and in_vertex_element:
            # vertex element を抜けた
            in_vertex_element = False

        elif in_vertex_element and line.startswith('property'):
            # 例: "property float x"
            parts = line.split()
            prop_name = parts[-1]
            vertex_properties.append(prop_name)

        elif line.startswith('end_header'):
            header_end_idx = i
            break

    if num_vertices is None or header_end_idx is None:
        raise ValueError(f"PLY ヘッダの解析に失敗しました: {path}")

    # 必要なプロパティのインデックスを取得
    try:
        idx_x = vertex_properties.index('x')
        idx_y = vertex_properties.index('y')
        idx_z = vertex_properties.index('z')
    except ValueError:
        raise ValueError(f"x/y/z プロパティが見つかりません: {path}")

    try:
        idx_curv = vertex_properties.index('curvature')
    except ValueError:
        raise ValueError(f"curvature プロパティが見つかりません: {path}")

    # ---- vertex データ読み込み ----
    x_list, y_list, z_list, curv_list = [], [], [], []

    start = header_end_idx + 1
    for i in range(num_vertices):
        line = lines[start + i].strip()
        if not line:
            continue
        parts = line.split()
        x_list.append(float(parts[idx_x]))
        y_list.append(float(parts[idx_y]))
        z_list.append(float(parts[idx_z]))
        curv_list.append(float(parts[idx_curv]))

    x = np.array(x_list)
    y = np.array(y_list)
    z = np.array(z_list)
    curvature = np.array(curv_list)

    return x, y, z, curvature


def compute_cumulative_length(x, y, z):
    """
    3次元座標列から累積長さ（arc length）を計算
    """
    pts = np.column_stack([x, y, z])  # shape (N, 3)
    diffs = pts[1:] - pts[:-1]        # shape (N-1, 3)
    seg_len = np.linalg.norm(diffs, axis=1)  # 各区間の長さ
    cum_len = np.concatenate([[0.0], np.cumsum(seg_len)])
    return cum_len


def main():
    # ---- ディレクトリ選択ダイアログ ----
    root = tk.Tk()
    root.withdraw()  # Tk ウィンドウを表示しない
    directory = filedialog.askdirectory(title="PLY ファイルが入っているディレクトリを選択してください")
    root.destroy()

    if not directory:
        print("ディレクトリが選択されませんでした。終了します。")
        return

    # ディレクトリ内の .ply ファイル一覧
    ply_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith('.ply')
    ]

    if not ply_files:
        print("指定ディレクトリに .ply ファイルが見つかりませんでした。")
        return

    plt.figure(figsize=(10, 6))

    max_length = 0.0

    for path in sorted(ply_files):
        try:
            x, y, z, curvature = read_ply_vertex_data(path)
            s = compute_cumulative_length(x, y, z)  # 累積長さ

            # このファイルの最大長さをチェック
            if s[-1] > max_length:
                max_length = s[-1]

            #label = os.path.basename(path)
            #plt.plot(s, curvature, label=label)
            plt.plot(s, curvature)
        except Exception as e:
            print(f"ファイルの処理中にエラー: {path}")
            print("  ->", e)

    print("max_lebgth=",max_length)
    plt.xlabel("Cumulative length")
    plt.ylabel("Curvature")
    plt.title("Cumulative length vs curvature (all PLY files)")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()
    plt.xlim(0, 100)      # 累積長さの範囲を 0〜100 に固定
    plt.ylim(0.0, 1.5)
    plt.show()


if __name__ == "__main__":
    main()
