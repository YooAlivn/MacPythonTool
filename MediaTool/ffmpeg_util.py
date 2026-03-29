import os
import subprocess
import time


class FfmpegUtil:
    def __init__(self, ffmpeg_exe=r"/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", input_path=None,
                 output_path=None):
        self.ffmpeg_exe = ffmpeg_exe  # ffmpeg安装目录
        self.input_path = input_path  # 输入文件或者文件夹地址
        self.output_path = output_path  # 输出文件或者文件夹地址

    @staticmethod
    def run_ffmpeg_command(command, msg):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] cmd: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {result.stdout}")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {result.stderr}")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 命令执行失败")
        return result.returncode

    # 从video中提取audio mp3
    def extract_audio_from_video(self, audio_format="mp3"):
        audio_output_path = os.path.join(self.output_path, f"temp_audio_{time.strftime('%Y%m%d%H%M%S')}.{audio_format}")
        """用ffmpeg提取音频（替代moviepy）"""
        try:
            # ffmpeg命令：-i 输入视频 -vn 只提取音频 -y 覆盖已有文件
            cmd = f'{self.ffmpeg_exe} -i "{self.input_path}" -vn -acodec {audio_format} -y "{audio_output_path}"'
            subprocess.run(cmd, shell=True, check=True)
            print(f"音频提取完成，保存至：{audio_output_path}")
            return audio_output_path
        except subprocess.CalledProcessError as e:
            print(f"音频提取失败（ffmpeg错误）：{e}")
            return None
        except Exception as e:
            print(f"音频提取失败：{e}")
            return None

    def merge_srt_with_video(self, video_path, srt_path, srt_output):
        cmd = f"{self.ffmpeg_exe} -y -i {video_path} -vf \"subtitles='{srt_path}'\" {srt_output}"
        return_code = self.run_ffmpeg_command(cmd, '视频和字幕合并成功')
        if return_code == 0:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 执行完成")
            return srt_output
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {return_code}")
        return None
