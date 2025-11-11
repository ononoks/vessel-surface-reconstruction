@echo off
setlocal

rem ===== 設定ここから =====
rem exe の場所（この bat と同じフォルダにある場合）
set "EXE=%~dp0VTKBinaryToAscii.exe"

rem 入力フォルダ（バイナリ VTK が入っているディレクトリ）
set "INPUT_DIR=D:\vessel-surface-reconstruction\TubeFromCenterline\data\10_siphon(MCA_ICA)"

rem 出力フォルダ
set "OUTPUT_DIR=%INPUT_DIR%\output_vtkAscii"
rem ===== 設定ここまで =====

if not exist "%EXE%" (
    echo ERROR: "%EXE%" が見つかりません。
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

for %%F in ("%INPUT_DIR%\*.vtk") do (
    echo Converting "%%~nxF" ...
    "%EXE%" "%%F" "%OUTPUT_DIR%\%%~nF_ascii.vtk"
    if errorlevel 1 (
        echo   -> ERROR: 変換に失敗しました。
    )
)

echo.
echo すべての変換処理が終了しました。
pause
endlocal
