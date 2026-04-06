# MacPythonTool
pyinstaller -F -w -n yutobedownloader YtdlpDownloader.py

--add-binary "tools/ffmpeg:tools" --add-binary "tools/ffprobe:tools"

pyinstaller --add-binary "ffmpegfull/ffmpeg:ffmpegfull" --add-binary "ffmpegfull/ffprobe:ffmpegfull" -F -w -n yutobedownloader YtdlpDownloader.py