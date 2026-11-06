#!/bin/bash
# whisper.cpp para el Celeron N2840 (sin AVX), mismas banderas que compilar_llama_wsl.sh. Salida: ~/candy_build/whisper_out
set -e
mkdir -p ~/candy_build && cd ~/candy_build
[ -d whisper.cpp ] || git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
git log --oneline -1
cmake -B build-candy -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF \
  -DGGML_NATIVE=OFF -DGGML_SSE42=ON -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF -DGGML_FMA=OFF \
  -DGGML_F16C=OFF -DGGML_BMI2=OFF -DGGML_OPENMP=OFF -DWHISPER_SDL2=OFF \
  -DCMAKE_C_FLAGS="-march=silvermont -mtune=silvermont" -DCMAKE_CXX_FLAGS="-march=silvermont -mtune=silvermont" \
  -DCMAKE_EXE_LINKER_FLAGS="-static-libstdc++ -static-libgcc" > /tmp/whisper_cmake.log
cmake --build build-candy -j 8 --target whisper-cli whisper-server > /tmp/whisper_build.log
mkdir -p ~/candy_build/whisper_out
cp build-candy/bin/whisper-cli build-candy/bin/whisper-server ~/candy_build/whisper_out/
echo "AVX en el binario (debe ser 0):"; objdump -d ~/candy_build/whisper_out/whisper-cli | grep -c -E 'ymm|zmm' || true
[ -f ~/candy_build/whisper_out/ggml-tiny.en.bin ] || bash models/download-ggml-model.sh tiny.en ~/candy_build/whisper_out > /dev/null
[ -f ~/candy_build/whisper_out/ggml-base.en.bin ] || bash models/download-ggml-model.sh base.en ~/candy_build/whisper_out > /dev/null
ls -la ~/candy_build/whisper_out
