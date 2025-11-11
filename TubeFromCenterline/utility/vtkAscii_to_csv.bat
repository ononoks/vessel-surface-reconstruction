@echo off
setlocal

rem ===== 設定ここから =====
rem Python 実行コマンド（必要なら python.exe のフルパスに変更）
set "PYTHON=python"

rem vtk_to_csv.py のパス（この bat と同じフォルダにある想定）
set "SCRIPT=%~dp0vtkAscii_to_csv.py"

rem VTK ASCII ファイルが置いてあるディレクトリ
set "INPUT_DIR=D:\vessel-surface-reconstruction\TubeFromCenterline\data\10_siphon(MCA_ICA)\output_vtkAscii"

rem 出力 CSV フォルダ（INPUT_DIR の親フォルダと同じ階層に output_csv を作る）
for %%A in ("%INPUT_DIR%\..") do set "OUTPUT_DIR=%%~fA\output_csv"
rem ===== 設定ここまで =====

if not exist "%SCRIPT%" (
    echo ERROR: "%SCRIPT%" が見つかりません。
    pause
    exit /b 1
)

if not exist "%INPUT_DIR%" (
    echo ERROR: 入力フォルダ "%INPUT_DIR%" が見つかりません。
    pause
    exit /b 1
)

if not exist "%OUTPUT_DIR%" (
    echo 出力フォルダ "%OUTPUT_DIR%" を作成します。
    mkdir "%OUTPUT_DIR%"
)

echo.
echo 入力フォルダ: "%INPUT_DIR%"
echo 出力フォルダ: "%OUTPUT_DIR%"
echo.

rem *.vtk を順に処理
for %%F in ("%INPUT_DIR%\*.vtk") do (
    echo Converting "%%~nxF" ...

    rem Python スクリプトを CLI モードで実行
    "%PYTHON%" "%SCRIPT%" "%%F"

    rem Python スクリプトは同じディレクトリに CSV を出すので、
    rem それを output_csv フォルダに移動
    if exist "%%~dpF%%~nF.csv" (
        move /Y "%%~dpF%%~nF.csv" "%OUTPUT_DIR%\"
    ) else (
        echo   -> WARNING: "%%~nxF" に対応する CSV が見つかりません。
    )
)

echo.
echo すべての変換処理が終了しました。
pause
endlocal
