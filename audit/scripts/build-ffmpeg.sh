#!/usr/bin/env bash
set -euxo pipefail
export PATH="/usr/bin:/c/Program Files (x86)/mingw64/bin:$PATH"
cd "$(dirname "$0")/.."
root="$PWD"
mkdir -p prefix/ffmpeg
if [ ! -d build/ffmpeg-native ]; then cp -r sources/ffmpeg-6.1.2 build/ffmpeg-native; fi
cd build/ffmpeg-native
./configure \
 --prefix=../../prefix/ffmpeg --target-os=mingw32 --arch=x86_64 \
 --disable-autodetect --disable-everything --disable-static --enable-shared \
 --disable-doc --disable-debug --disable-x86asm --disable-network \
 --disable-avdevice --disable-postproc --disable-ffplay \
 --enable-ffmpeg --enable-ffprobe --enable-avcodec --enable-avformat \
 --enable-avfilter --enable-swscale --enable-swresample \
 --enable-decoder=vp9 --enable-parser=vp9 --enable-demuxer=matroska \
 --enable-protocol=file,pipe --enable-muxer=null --enable-encoder=wrapped_avframe \
 --enable-filter=buffer,buffersink,null,format,scale
mingw32-make -j8 SHELL='C:/Program Files/Git/bin/bash.exe'
mingw32-make install SHELL='C:/Program Files/Git/bin/bash.exe'
