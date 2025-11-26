# setup
https://qiita.com/ononono73/items/f336cea22c3f0813406d

# usage
ビルドは `x64 Native Tools Command Prompt for VS 2022` で行う必要がある <br>
Copy `TubeFromCenterline.cpp` and `CMakeLists.txt` in your directory, and build by below commands
```
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

and execute <br>
(実行は、どのCLIでもいい)
```
cd Release
.\TubeFromCenterline.exe
```

# memo

菅軸方向の分割数は、読み込む中心線(*.csv) の点群数で決まる <br>
血管半径と円周方向の分割数は、コード内の
```
double tubeRadius = 0.8;
const unsigned int nTv = 64;
```
で制御しており、実行時に入力できる。
