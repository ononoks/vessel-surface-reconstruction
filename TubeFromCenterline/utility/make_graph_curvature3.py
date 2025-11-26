import os
import numpy as np
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog

def read_ply_vertex_data(path):
    """PLYからvertex部分のみ読み込み、x, y, z, curvatureを返す"""
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    num_vertices = None
    in_vertex_element = False
    vertex_properties = []
    header_end_idx = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        parts = line.split()

        # element vertex N のみマッチ（vertex_seqを除外）
        if len(parts) >= 3 and parts[0] == 'element' and parts[1] == 'vertex':
            num_vertices = int(parts[2])
            in_vertex_element = True
        elif parts[0] == 'element' and in_vertex_element:
            in_vertex_element = False
        elif in_vertex_element and parts[0] == 'property':
            vertex_properties.append(parts[-1])
        elif parts[0] == 'end_header':
            header_end_idx = i
            break

    if num_vertices is None or header_end_idx is None:
        raise ValueError(f"PLYヘッダ解析に失敗: {path}")

    # 各プロパティの列番号
    idx_x = vertex_properties.index('x')
    idx_y = vertex_properties.index('y')
    idx_z = vertex_properties.index('z')
    idx_curv = vertex_properties.index('curvature')

    # 頂点データ読込
    start = header_end_idx + 1
    x, y, z, curvature = [], [], [], []
    for i in range(num_vertices):
        parts = lines[start + i].split()
        x.append(float(parts[idx_x]))
        y.append(float(parts[idx_y]))
        z.append(float(parts[idx_z]))
        curvature.append(float(parts[idx_curv]))

    return np.array(x), np.array(y), np.array(z), np.array(curvature)


def compute_cumulative_length(x, y, z):
    """3次元座標列から累積長さ（arc length）を計算"""
    pts = np.column_stack([x, y, z])
    if pts.shape[0] <= 1:
        return np.array([0.0])
    seg_len = np.linalg.norm(pts[1:] - pts[:-1], axis=1)
    cum_len = np.concatenate([[0.0], np.cumsum(seg_len)])
    return cum_len


def main():
    # ---- ディレクトリ選択 ----
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="PLYファイルのあるディレクトリを選択")
    root.destroy()
    if not directory:
        print("ディレクトリ未選択 → 終了します。")
        return

    ply_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith('.ply')]
    if not ply_files:
        print("指定ディレクトリに .ply ファイルが見つかりません。")
        return

    plt.figure(figsize=(10, 6))
    max_length = 0.0
    legend_candidates = []  # (max_curv, line_handle, label)

    for path in sorted(ply_files):
        try:
            x, y, z, curvature = read_ply_vertex_data(path)
            s = compute_cumulative_length(x, y, z)
            line, = plt.plot(s, curvature, linewidth=0.8, alpha=0.8)

            max_curv = float(np.max(curvature))
            label = os.path.basename(path)
            legend_candidates.append((max_curv, line, label))

            if s[-1] > max_length:
                max_length = s[-1]

        except Exception as e:
            print(f"エラー: {path}\n  -> {e}")

    plt.xlabel("Cumulative length")
    plt.ylabel("Curvature")
    plt.title(f"Cumulative length vs curvature ({len(ply_files)} files)")
    plt.grid(True)
    plt.tight_layout()
    plt.xlim(0, max_length)

    # ---- 上位10本のファイルを抽出 ----
    if legend_candidates:
        legend_candidates.sort(key=lambda t: t[0], reverse=True)
        top10 = legend_candidates[:10]

        # グラフ凡例（上位10本のみ）
        handles = [t[1] for t in top10]
        labels = [t[2] for t in top10]
        plt.legend(handles, labels, fontsize=8, title="Top 10 by max curvature")

        # コンソール出力
        print("\n=== Curvature 最大値 上位10ファイル ===")
        for rank, (max_curv, _, label) in enumerate(top10, start=1):
            print(f"{rank:2d}. {label:<30s}  max curvature = {max_curv:.6f}")

    print(f"\nmax_length = {max_length:.3f}")
    plt.show()


if __name__ == "__main__":
    main()
