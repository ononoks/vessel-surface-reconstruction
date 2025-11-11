#include <vtkDataSet.h>
#include <vtkDataSetReader.h>
#include <vtkDataSetWriter.h>
#include <vtkNew.h>

#include <iostream>
#include <string>

#if defined(_WIN32)
// Windows のファイルダイアログ用
#include <windows.h>
#include <commdlg.h>
#include <filesystem>
#include <cstdio>

// 入力 VTK ファイルを選ぶダイアログ
static std::string OpenVTKFileDialog()
{
    char fileBuf[MAX_PATH] = "";
    OPENFILENAMEA ofn{};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner   = nullptr;
    ofn.lpstrFilter = "VTK Files (*.vtk)\0*.vtk\0All Files (*.*)\0*.*\0";
    ofn.lpstrFile   = fileBuf;
    ofn.nMaxFile    = MAX_PATH;
    ofn.Flags       = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;

    if (GetOpenFileNameA(&ofn))
    {
        return std::string(fileBuf);
    }
    return std::string();
}

// 出力 VTK ファイルを選ぶダイアログ
static std::string SaveVTKFileDialog(const std::string& defaultName)
{
    char fileBuf[MAX_PATH] = "";
    std::snprintf(fileBuf, MAX_PATH, "%s", defaultName.c_str());

    OPENFILENAMEA ofn{};
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner   = nullptr;
    ofn.lpstrFilter = "VTK Files (*.vtk)\0*.vtk\0All Files (*.*)\0*.*\0";
    ofn.lpstrFile   = fileBuf;
    ofn.nMaxFile    = MAX_PATH;
    ofn.Flags       = OFN_OVERWRITEPROMPT;
    ofn.lpstrDefExt = "vtk"; // 拡張子補完

    if (GetSaveFileNameA(&ofn))
    {
        return std::string(fileBuf);
    }
    return std::string();
}
#endif // _WIN32

// 実際の変換処理
static bool ConvertBinaryVTKToASCII(const std::string& inputFile,
                                    const std::string& outputFile)
{
    vtkNew<vtkDataSetReader> reader;
    reader->SetFileName(inputFile.c_str());
    reader->ReadAllScalarsOn();
    reader->ReadAllVectorsOn();
    reader->ReadAllTensorsOn();
    reader->ReadAllFieldsOn();

    std::cout << "Reading: " << inputFile << std::endl;
    reader->Update();

    vtkDataSet* data = reader->GetOutput();
    if (!data)
    {
        std::cerr << "Failed to read dataset from: " << inputFile << std::endl;
        return false;
    }

    vtkNew<vtkDataSetWriter> writer;
    writer->SetFileName(outputFile.c_str());
    writer->SetInputData(data);
    writer->SetFileTypeToASCII();  // ← ASCII 形式で出力

    std::cout << "Writing ASCII VTK: " << outputFile << std::endl;
    if (!writer->Write())
    {
        std::cerr << "Failed to write ASCII VTK to: " << outputFile << std::endl;
        return false;
    }

    std::cout << "Conversion finished successfully." << std::endl;
    return true;
}

int main(int argc, char* argv[])
{
    std::string inputFile;
    std::string outputFile;

#if defined(_WIN32)
    // Windows:
    //   - 引数が 2つ (input, output) あればそれを使う
    //   - 引数が足りなければ GUI ダイアログで選択
    if (argc < 3)
    {
        inputFile = OpenVTKFileDialog();
        if (inputFile.empty())
        {
            std::cerr << "Input file was not selected. Exiting." << std::endl;
            return EXIT_FAILURE;
        }

        // デフォルト出力ファイル名: inputFile の末尾に "_ascii.vtk" を付ける
        std::filesystem::path inPath(inputFile);
        std::string defaultOut =
            (inPath.parent_path() / (inPath.stem().string() + "_ascii.vtk")).string();

        outputFile = SaveVTKFileDialog(defaultOut);
        if (outputFile.empty())
        {
            std::cerr << "Output file was not selected. Exiting." << std::endl;
            return EXIT_FAILURE;
        }
    }
    else
    {
        inputFile  = argv[1];
        outputFile = argv[2];
    }
#else
    // macOS / Linux: コマンドライン引数で指定
    if (argc < 3)
    {
        std::cerr << "Usage: " << argv[0]
                  << " input_binary.vtk output_ascii.vtk" << std::endl;
        return EXIT_FAILURE;
    }
    inputFile  = argv[1];
    outputFile = argv[2];
#endif

    if (!ConvertBinaryVTKToASCII(inputFile, outputFile))
    {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
