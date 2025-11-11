import os
import re
import math
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import pandas as pd


def parse_vtk_points_and_radius(vtk_path):
    """
    VTK(ASCII, POLYDATA)から
    - 点座標 (N,3) ndarray
    - MaximumInscribedSphereRadius (N,) ndarray
    を取り出す
    """
    with open(vtk_path, "r") as f:
        text = f.read()

    # ---- POINTS ブロックを抽出 ----
    m_points = re.search(r"POINTS\s+(\d+)\s+\w+\s*([\s\S]*)", text)
    if not m_points:
        raise ValueError("VTK内に POINTS ブロックが見つかりません。")

    n_points = int(m_points.group(1))
    tail = m_points.group(2)

    # 次のキーワードまでを切り出す
    m_next = re.search(
        r"\n(?:VERTICES|LINES|POLYGONS|TRIANGLE_STRIPS|POINT_DATA|CELL_DATA)\b",
        tail
    )
    if m_next:
        points_text = tail[:m_next.start()]
    else:
        points_text = tail

    # 数値に変換
    point_nums = [float(v) for v in points_text.split()]
    if len(point_nums) < 3 * n_points:
        raise ValueError("POINTS の数値が指定数より少ないようです。")
    point_nums = point_nums[: 3 * n_points]

    points = np.array(point_nums, dtype=float).reshape(-1, 3)

    # ---- POINT_DATA & MaximumInscribedSphereRadius を抽出 ----
    m_pd = re.search(r"POINT_DATA\s+(\d+)", text)
    if not m_pd:
        raise ValueError("VTK内に POINT_DATA ブロックが見つかりません。")

    # MaximumInscribedSphereRadius スカラーフィールドを探す
    m_scalar = re.search(
        r"POINT_DATA\s+\d+[\s\S]*?SCALARS\s+MaximumInscribedSphereRadius\s+\w+[\r\n]+LOOKUP_TABLE\s+\w+([\s\S]*)",
        text
    )
    if not m_scalar:
        raise ValueError("SCALARS MaximumInscribedSphereRadius が見つかりません。")

    tail_scalar = m_scalar.group(1)

    # 次の CELL_DATA または 別の SCALARS まで
    m_stop = re.search(r"\n(?:CELL_DATA\b|SCALARS\b)", tail_scalar)
    if m_stop:
        scalar_text = tail_scalar[:m_stop.start()]
    else:
        scalar_text = tail_scalar

    scalar_nums = [float(v) for v in scalar_text.split()]
    if len(scalar_nums) < n_points:
        raise ValueError("MaximumInscribedSphereRadius の個数が POINT_DATA の点数より少ないようです。")
    scalar_nums = scalar_nums[:n_points]

    radius = np.array(scalar_nums, dtype=float)

    if points.shape[0] != radius.shape[0]:
        raise ValueError("点数と MaximumInscribedSphereRadius の数が一致しません。")

    return points, radius


def compute_nearest(points_csv, points_vtk, radius_vtk):
    """
    CSVの各点(points_csv: (M,3))に対して、
    VTKの点(points_vtk: (N,3))の最近接点を探し、
    距離とその点のradius(MaximumInscribedSphereRadius)を返す。
    """
    M = points_csv.shape[0]
    N = points_vtk.shape[0]

    distances = np.zeros(M, dtype=float)
    radii = np.zeros(M, dtype=float)

    # 単純な最近傍探索（M×N）。データ数が極端でなければ十分高速。
    for i in range(M):
        diff = points_vtk - points_csv[i]
        dist2 = np.sum(diff * diff, axis=1)
        idx = int(np.argmin(dist2))
        distances[i] = math.sqrt(dist2[idx])
        radii[i] = radius_vtk[idx]

    return radii, distances


def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("CSV + VTK 最近接情報付加", "まず、座標CSVファイル (x,y,z) を選択してください。")

    csv_path = filedialog.askopenfilename(
        title="座標CSVファイルを選択",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )

    if not csv_path:
        messagebox.showwarning("キャンセル", "CSVファイルが選択されませんでした。")
        return

    messagebox.showinfo("VTKファイル選択", "次に、VTK ASCII ファイルを選択してください。")

    vtk_path = filedialog.askopenfilename(
        title="VTKファイルを選択",
        filetypes=[("VTK files", "*.vtk"), ("All files", "*.*")]
    )

    if not vtk_path:
        messagebox.showwarning("キャンセル", "VTKファイルが選択されませんでした。")
        return

    try:
        # CSV読み込み
        df = pd.read_csv(csv_path)

        # x, y, z カラムの取得（名前が違う場合は先頭3列を使う）
        for_candidate = [c.lower() for c in df.columns]
        if all(col in for_candidate for col in ["x", "y", "z"]):
            # 大文字/小文字を気にせずマッピング
            col_map = {c.lower(): c for c in df.columns}
            x_col = col_map["x"]
            y_col = col_map["y"]
            z_col = col_map["z"]
        else:
            # 先頭3列を x,y,z とみなす
            x_col, y_col, z_col = df.columns[:3]

        points_csv = df[[x_col, y_col, z_col]].to_numpy(dtype=float)

        # VTK から点と MaximumInscribedSphereRadius を取得
        points_vtk, radius_vtk = parse_vtk_points_and_radius(vtk_path)

        # 最近接点探索
        radii, distances = compute_nearest(points_csv, points_vtk, radius_vtk)

        # 新しい列を追加
        df["radius"] = radii
        df["distance"] = distances

        # 出力ファイル名（元CSVと同じ場所・ファイル名に_suffixを追加）
        base, ext = os.path.splitext(csv_path)
        out_path = base + "_with_radius_distance.csv"

        df.to_csv(out_path, index=False)

        messagebox.showinfo("完了", f"新しいCSVを保存しました。\n{out_path}")

    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")


if __name__ == "__main__":
    main()
