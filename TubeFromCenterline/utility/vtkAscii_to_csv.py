import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys  # ← 追加

def vtk_to_csv(vtk_path):
    """VTKファイルを読み取り、x,y,z座標をCSVに変換"""
    with open(vtk_path, "r") as f:
        vtk_text = f.read()

    # POINTSセクションを正規表現で抽出
    match = re.search(r"POINTS\s+\d+\s+\w+\s+([\s\S]*?)(?:\n[A-Z]|$)", vtk_text)
    if not match:
        raise ValueError("POINTS セクションが見つかりません。")

    points_text = match.group(1)

    # 数値を抽出して3列ごとにグループ化
    numbers = [float(n) for n in points_text.split()]
    if len(numbers) % 3 != 0:
        raise ValueError("POINTS の数値が3の倍数ではありません。")

    points = [numbers[i:i+3] for i in range(0, len(numbers), 3)]
    df = pd.DataFrame(points, columns=["x", "y", "z"])

    # 出力ファイル名を決定
    base = os.path.splitext(vtk_path)[0]
    csv_path = base + ".csv"

    # CSV出力
    df.to_csv(csv_path, index=False)
    return csv_path


def main_gui():
    """GUIでVTKファイルを選択してCSVに変換"""
    root = tk.Tk()
    root.withdraw()  # メインウィンドウ非表示

    messagebox.showinfo("VTK → CSV 変換", "変換したい VTK ファイルを選択してください。")

    # ファイル選択ダイアログ
    vtk_path = filedialog.askopenfilename(
        title="VTKファイルを選択",
        filetypes=[("VTK files", "*.vtk"), ("All files", "*.*")]
    )

    if not vtk_path:
        messagebox.showwarning("キャンセル", "ファイルが選択されませんでした。")
        return

    try:
        csv_path = vtk_to_csv(vtk_path)
        messagebox.showinfo("完了", f"CSVファイルを出力しました：\n{csv_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"変換中にエラーが発生しました：\n{e}")


def main():
    # 1個以上の引数がある場合は、CLIモードで処理（Tk は使わない）
    if len(sys.argv) > 1:
        for vtk_path in sys.argv[1:]:
            try:
                csv_path = vtk_to_csv(vtk_path)
                print(f"Converted: {vtk_path} -> {csv_path}")
            except Exception as e:
                print(f"Error converting {vtk_path}: {e}")
        return

    # 引数がない場合は従来通り GUI モード
    main_gui()


if __name__ == "__main__":
    main()
