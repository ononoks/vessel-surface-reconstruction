#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
バイナリ形式の legacy VTK (*.vtk) ファイルを読み込み、
ASCII 形式の legacy VTK (*.vtk) として保存するスクリプト（GUI版）。

- 起動するとファイル選択ダイアログが開くので、入力 .vtk を選択する。
- 続いて、出力ファイル名を指定するダイアログが開く。
"""

import os
import sys

# --- VTK 読み込み ---
try:
    import vtk
except ImportError:
    print("vtk モジュールが見つかりません。先に 'pip install vtk' を実行してください。")
    sys.exit(1)

# --- Tkinter でファイルダイアログ ---
import tkinter as tk
from tkinter import filedialog, messagebox


def convert_binary_vtk_to_ascii(input_path: str, output_path: str) -> None:
    # 入力ファイル存在チェック
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")

    # legacy VTK 用のリーダー
    reader = vtk.vtkDataSetReader()
    reader.SetFileName(input_path)
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.ReadAllTensorsOn()
    reader.ReadAllFieldsOn()

    print(f"読み込み中: {input_path}")
    reader.Update()

    data = reader.GetOutput()
    if data is None:
        raise RuntimeError("VTK ファイルからデータを取得できませんでした。legacy VTK 形式か確認してください。")

    # DataSetWriter を使って ASCII 形式で書き出し
    writer = vtk.vtkDataSetWriter()
    writer.SetFileName(output_path)
    writer.SetInputData(data)
    writer.SetFileTypeToASCII()  # ← ここで ASCII 指定

    print(f"書き出し中 (ASCII): {output_path}")
    if writer.Write() == 0:
        raise RuntimeError("VTK ファイルの書き出しに失敗しました。")

    print("変換完了。")


def main():
    # Tk のルートウィンドウ（非表示）
    root = tk.Tk()
    root.withdraw()

    # --- 入力ファイル選択 ---
    input_path = filedialog.askopenfilename(
        title="バイナリ形式の VTK ファイルを選択してください",
        filetypes=[("VTK files", "*.vtk"), ("All files", "*.*")]
    )

    if not input_path:
        # キャンセル
        print("入力ファイルが選択されませんでした。終了します。")
        return

    # デフォルト出力ファイル名を作る
    base, ext = os.path.splitext(input_path)
    default_output = base + "_ascii.vtk"

    # --- 出力ファイル名選択 ---
    output_path = filedialog.asksaveasfilename(
        title="ASCII 形式 VTK の保存先を選択してください",
        initialfile=os.path.basename(default_output),
        defaultextension=".vtk",
        filetypes=[("VTK files", "*.vtk"), ("All files", "*.*")]
    )

    if not output_path:
        print("出力ファイルが指定されませんでした。終了します。")
        return

    try:
        convert_binary_vtk_to_ascii(input_path, output_path)
    except Exception as e:
        messagebox.showerror("エラー", f"変換中にエラーが発生しました。\n{e}")
        print("エラー:", e)
        return

    messagebox.showinfo("完了", "変換が正常に完了しました。")
    print("変換が正常に完了しました。")


if __name__ == "__main__":
    main()
