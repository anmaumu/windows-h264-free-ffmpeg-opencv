$ErrorActionPreference = 'Stop'
$AuditRoot = Split-Path $PSScriptRoot -Parent
$Py = "$AuditRoot\.venv\Scripts\python.exe"
$CMake = "$AuditRoot\.venv\Scripts\cmake.exe"
$Ninja = "$AuditRoot\.venv\Scripts\ninja.exe"
$Src = "$AuditRoot\sources\opencv-4.10.0"
$Build = "$AuditRoot\build\opencv-mingw2"
$Install = "$AuditRoot\prefix\opencv"
$PythonRoot = (Resolve-Path "$AuditRoot\.venv").Path
$BasePython = & $Py -c 'import sys; print(sys.base_prefix)'
$Numpy = & $Py -c 'import numpy; print(numpy.get_include())'
$AuditCmake = ($AuditRoot -replace '\\','/') + '/cmake'
$PyCmake = $Py -replace '\\','/'
$BasePythonCmake = $BasePython -replace '\\','/'
$NumpyCmake = $Numpy -replace '\\','/'
$PythonRootCmake = $PythonRoot -replace '\\','/'
New-Item -ItemType Directory -Force $Build | Out-Null
$ErrorActionPreference = 'Continue'
& $CMake -S $Src -B $Build -G Ninja `
  "-DCMAKE_MAKE_PROGRAM=$Ninja" `
  '-DCMAKE_C_COMPILER=C:/Program Files (x86)/mingw64/bin/gcc.exe' `
  '-DCMAKE_CXX_COMPILER=C:/Program Files (x86)/mingw64/bin/g++.exe' `
  "-DCMAKE_INSTALL_PREFIX=$Install" `
  "-DCMAKE_MODULE_PATH=$AuditCmake" `
  '-DOPENCV_FFMPEG_USE_FIND_PACKAGE=FFMPEG' '-DOPENCV_FFMPEG_SKIP_DOWNLOAD=ON' `
  '-DBUILD_LIST=core,imgproc,videoio,python3' '-DBUILD_SHARED_LIBS=ON' `
  '-DBUILD_TESTS=OFF' '-DBUILD_PERF_TESTS=OFF' '-DBUILD_EXAMPLES=OFF' '-DBUILD_opencv_apps=OFF' `
  '-DWITH_MSMF=OFF' '-DWITH_DSHOW=OFF' '-DWITH_OPENCL=OFF' '-DWITH_IPP=OFF' `
  "-DPYTHON3_EXECUTABLE=$PyCmake" "-DPYTHON3_INCLUDE_DIR=$BasePythonCmake/include" `
  "-DPYTHON3_LIBRARY=$BasePythonCmake/libs/python312.lib" "-DPYTHON3_NUMPY_INCLUDE_DIRS=$NumpyCmake" `
  "-DPYTHON3_PACKAGES_PATH=$PythonRootCmake/Lib/site-packages" `
  *> "$AuditRoot\logs\opencv-configure.txt"
if ($LASTEXITCODE -ne 0) { throw 'OpenCV configure failed' }
& $CMake --build $Build --parallel 8 *> "$AuditRoot\logs\opencv-build.txt"
if ($LASTEXITCODE -ne 0) { throw 'OpenCV build failed' }
& $CMake --install $Build *> "$AuditRoot\logs\opencv-install.txt"
if ($LASTEXITCODE -ne 0) { throw 'OpenCV install failed' }
