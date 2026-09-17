set(_ffroot "${CMAKE_CURRENT_LIST_DIR}/../prefix/ffmpeg")
get_filename_component(_ffroot "${_ffroot}" ABSOLUTE)
set(FFMPEG_INCLUDE_DIRS "${_ffroot}/include")
set(FFMPEG_LIBRARIES
  "${_ffroot}/bin/avformat.lib"
  "${_ffroot}/bin/avcodec.lib"
  "${_ffroot}/bin/avutil.lib"
  "${_ffroot}/bin/swscale.lib"
  "${_ffroot}/bin/swresample.lib")
set(FFMPEG_libavcodec_VERSION "60.31.102")
set(FFMPEG_libavformat_VERSION "60.16.100")
set(FFMPEG_libavutil_VERSION "58.29.100")
set(FFMPEG_libswscale_VERSION "7.5.100")
set(FFMPEG_FOUND TRUE)
