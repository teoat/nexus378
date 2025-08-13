@echo off
setlocal EnableDelayedExpansion

if "%gpu_variant:~0,5%"=="cuda-" (
    set CMAKE_ARGS=!CMAKE_ARGS! -DCMAKE_CUDA_ARCHITECTURES=all-major
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_CUDA=ON
) else (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_CUDA=OFF
)

if "%blas_impl%"=="mkl" (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_BLAS=ON
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_ACCELERATE=OFF
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_BLAS_VENDOR=Intel10_64_dyn
) else if "%blas_impl%"=="openblas" (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_BLAS=ON
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_ACCELERATE=OFF
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_BLAS_VENDOR=OpenBLAS
) else (
    REM Note: LLAMA_CUDA=ON enables cublas.
    REM Tests fail when both mkl and cublas are used.
    REM This has also been reported here: https://github.com/ggerganov/llama.cpp/issues/4626
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_BLAS=OFF
)

REM This section configures CPU optimization flags based on the x86_64_opt variable:
REM - "v3" enables AVX and AVX2 for both GGML and MSVC (suitable for modern CPUs)
REM - "v2" enables only AVX for both GGML and MSVC (for CPUs with AVX but not AVX2)
REM - Any other value disables both AVX and AVX2 (for older or compatible builds)
REM The ARCH_FLAG is set accordingly to ensure MSVC doesn't implicitly enable 
REM higher instruction sets. AVX-512 is explicitly disabled in all cases.

REM AVX2 when enabled can implicitly enable AVX-512 instructions within msvc so 
REM we disable AVX-512 explicitly and set AVX2 explicitly to ensure we don't get AVX-512.

if "%x86_64_opt%"=="v3" (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX=ON
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX2=ON
    REM set ARCH_FLAG=/arch:AVX2
) else if "%x86_64_opt%"=="v2" (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX=ON
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX2=OFF
    REM set ARCH_FLAG=/arch:AVX
) else (
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX=OFF
    set LLAMA_ARGS=!LLAMA_ARGS! -DGGML_AVX2=OFF
    REM set ARCH_FLAG=/arch:SSE2
)

set CXXFLAGS=!CXXFLAGS! !ARCH_FLAG!
set CFLAGS=!CFLAGS! !ARCH_FLAG!

cmake -S . -B build ^
    -G Ninja ^
    !CMAKE_ARGS! ^
    !LLAMA_ARGS! ^
    -DCMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
    -DCMAKE_PREFIX_PATH=%LIBRARY_PREFIX% ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DLLAMA_BUILD_TESTS=ON  ^
    -DBUILD_SHARED_LIBS=ON  ^
    -DGGML_NATIVE=OFF ^
    -DGGML_AVX512=OFF ^
    -DGGML_AVX512_VBMI=OFF ^
    -DGGML_AVX512_VNNI=OFF ^
    -DGGML_AVX512_BF16=OFF ^
    -DGGML_FMA=OFF ^
    -DGGML_CUDA_F16=OFF

REM in MSVC F16C is implied with AVX2/AVX512 so we can't enable/disable it via cmake

if errorlevel 1 exit 1

cmake --build build --config Release --verbose
if errorlevel 1 exit 1

cmake --install build
if errorlevel 1 exit 1

ctest --output-on-failure build -j%CPU_COUNT% --test-dir build/tests
if errorlevel 1 exit 1
