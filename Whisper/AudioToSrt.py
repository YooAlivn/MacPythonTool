import gc
import os
import subprocess
import sys
import time
from enum import Enum

import whisper
from datetime import timedelta

import TranslateOllama

VIDEO_MAIN = r"/Users/alvin/MediaSource/Yutobe/2026-04"
FFMPEG_PATH = r"/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
TRANSLATE_MODEL = "translategemma:4b"


class CommonParam(str, Enum):
    TRANSLATE_MODEL = sys.argv[1]
    FFMPEG_PATH = sys.argv[2]
    VIDEO_MAIN = sys.argv[3]
    file_name = sys.argv[4]
    need_original_lan_param = sys.argv[5]
    original_lan = sys.argv[6]
    target_lan = sys.argv[7]

def extract_audio_from_video(video_path,
                             audio_output_path=os.path.join(CommonParam.VIDEO_MAIN.value,
                                                            f"temp_audio_{time.strftime('%Y%m%d%H%M%S')}.mp3")):
    """用ffmpeg提取音频（替代moviepy）"""
    try:
        # ffmpeg命令：-i 输入视频 -vn 只提取音频 -y 覆盖已有文件
        cmd = f'{CommonParam.FFMPEG_PATH.value} -i "{video_path}" -vn -acodec mp3 -y "{audio_output_path}"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"音频提取完成，保存至：{audio_output_path}")
        return audio_output_path
    except subprocess.CalledProcessError as e:
        print(f"音频提取失败（ffmpeg错误）：{e}")
        return None
    except Exception as e:
        print(f"音频提取失败：{e}")
        return None


def format_timestamp(seconds):
    """将秒数转换为SRT字幕的时间格式（00:00:00,000）"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    ms = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def unload_whisper_model(model):
    if model:
        del model
    model = None
    # 强制垃圾回收
    gc.collect()

    # 清理特定设备的缓存
    # if self.device == "cuda" and torch.cuda.is_available():
    #     torch.cuda.empty_cache()
    #     print("✅ CUDA 缓存已清理")
    # elif self.device == "mps" and torch.backends.mps.is_available():
    #     # Mac MPS 需要特殊处理
    #     torch.mps.empty_cache()
    #     print("✅ MPS 缓存已清理")
    # else:
    #     print("✅ CPU 内存已释放")
    #     return False  # 不抑制异常


def speech_to_text(audio_path, model_name="large-v3-turbo"):
    """用whisper将音频转文字，返回带时间戳的文本列表"""
    # 加载whisper模型（base模型轻量，适合新手；large模型更精准但慢）
    model = whisper.load_model(download_root=r"/Users/alvin/MediaSource/Models", name=model_name)
    # 识别音频，输出带时间戳的segments
    result = model.transcribe(audio_path, verbose=False)
    segments = result["segments"]  # 每个segment包含start/end/text
    unload_whisper_model(model)
    # 清理识别的文本（去除多余空格）
    clean_segments = []
    for seg in segments:
        clean_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    print(f"语音识别完成，共识别{len(clean_segments)}段文字")
    return clean_segments


def translate_text(text):
    """翻译文字（默认翻译成中文）"""
    if not text:
        return ""
    try:
        translated = TranslateOllama.simple_translate(text,
                                                      model=CommonParam.TRANSLATE_MODEL.value,
                                                      original_lang=CommonParam.original_lan.value,
                                                      target_lang=CommonParam.target_lan.value)
        print(f"原文（{text}）")
        print(f"译文（{translated}）")
        return translated
    except Exception as e:
        print(f"翻译失败（{text}）：{e}")
        return text  # 翻译失败则返回原文


def generate_srt(segments,
                 srt_path=os.path.join(CommonParam.VIDEO_MAIN.value, f"output_subtitle_{time.strftime('%Y%m%d%H%M%S')}.srt")):
    """生成SRT字幕文件（包含原文+翻译）"""
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, 1):
            # 转换时间戳格式
            start_time = format_timestamp(seg["start"])
            end_time = format_timestamp(seg["end"])

            # 翻译文本
            original_text = seg["text"]
            translated_text = translate_text(original_text)

            # 写入SRT格式（序号 → 时间范围 → 字幕内容）
            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            if CommonParam.need_original_lan_param.value.strip() in ['Y', 'y']:
                f.write(f"{original_text}\n")
            f.write(f"{translated_text}\n\n")
    print(f"字幕文件生成完成：{srt_path}")
    return srt_path


def video_to_translated_subtitle(video_path, srt_output=os.path.join(CommonParam.VIDEO_MAIN.value, "translated_subtitle.srt")):
    """主函数：视频→音频→识别→翻译→字幕"""
    # 1. 提取音频
    audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        return

    # 2. 语音转文字（带时间戳）
    segments = speech_to_text(audio_path)
    if not segments:
        return

    # 3. 生成翻译后的字幕文件
    generate_srt(segments, srt_output)
    # 卸载模型释放内存
    TranslateOllama.unload_model(model=CommonParam.TRANSLATE_MODEL.value)

    # 清理临时音频文件
    if os.path.exists(audio_path):
        os.remove(audio_path)



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

def rm_file(path):
    if os.path.exists(path):
        os.remove(path)

def merge_srt_with_video(video_path, srt_path, srt_output):
    cmd = f"{CommonParam.FFMPEG_PATH.value} -y -i {video_path} -vf \"subtitles='{srt_path}'\" {srt_output}"
    returncode = run_ffmpeg_command(cmd, '视频和字幕合并成功')
    if returncode == 0:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 执行完成")

        rm_file(srt_path)
        # rm_file(video_path)

# ------------------- 执行示例 -------------------

if __name__ == '__main__':
    print(sys.argv)

    # 替换成你的视频文件路径（支持MP4、AVI、MKV等常见格式）
    VIDEO_FILE = os.path.join(CommonParam.VIDEO_MAIN.value, f"{CommonParam.file_name.value}.mp4")
    print(f"{VIDEO_FILE}")
    # 生成的字幕文件路径
    SRT_FILE = os.path.join(CommonParam.VIDEO_MAIN.value, f"translated_subtitle_{time.strftime('%Y%m%d%H%M%S')}.srt")

    # 运行主函数
    video_to_translated_subtitle(VIDEO_FILE, SRT_FILE)
    RES_FILE = os.path.join(CommonParam.VIDEO_MAIN.value, f"{CommonParam.file_name.value}_srt.mp4")
    # TODO 合成字幕和视频
    merge_srt_with_video(VIDEO_FILE, SRT_FILE, RES_FILE)

