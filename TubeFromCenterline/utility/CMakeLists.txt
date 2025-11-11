cmake_minimum_required(VERSION 3.12 FATAL_ERROR)
project(VTKTools LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(VTK REQUIRED COMPONENTS
  CommonCore
  CommonDataModel
  IOLegacy
)

if (NOT VTK_FOUND)
  message(FATAL_ERROR "Unable to find VTK")
endif()

add_executable(VTKBinaryToAscii VtkBinaryToAscii.cpp)
target_link_libraries(VTKBinaryToAscii PRIVATE ${VTK_LIBRARIES})

# Windows でファイルダイアログ (GetOpenFileName / GetSaveFileName) を使うため
if (WIN32)
  target_link_libraries(VTKBinaryToAscii PRIVATE comdlg32)
endif()

# vtk_module_autoinit は VTK 使用ターゲットに必須
vtk_module_autoinit(
  TARGETS VTKBinaryToAscii
  MODULES ${VTK_LIBRARIES}
)
