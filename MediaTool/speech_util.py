import gc
import os
import time

import whisper

from base_util import format_timestamp
from ollama_util import OllamaUtil
from ffmpeg_util import FfmpegUtil


class SpeechUtil:
    def __init__(self, whisper_model_name: str = "large-v3-turbo",
                 whisper_model_root: str = r"/Users/alvin/MediaSource/Models", out_path: str = ""):
        self.whisper_model_root = whisper_model_root
        self.whisper_model_name = whisper_model_name
        self.out_path = out_path

    def unload_whisper_model(self):
        if self.whisper_model_name:
            del self.whisper_model_name
        self.whisper_model_name = None
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

    def speech_to_text(self, audio_path):
        """用whisper将音频转文字，返回带时间戳的文本列表"""
        # 加载whisper模型（base模型轻量，适合新手；large模型更精准但慢）
        model = whisper.load_model(download_root=self.whisper_model_root, name=self.whisper_model_name)
        # 识别音频，输出带时间戳的segments
        result = model.transcribe(audio_path, verbose=False)
        segments = result["segments"]  # 每个segment包含start/end/text
        self.unload_whisper_model()
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

    @staticmethod
    def translate_text(text=None, current_language="en", model="translategemma:4b", target_language="cn",
                       ollama_host="192.168.7.110"):
        """翻译文字（默认翻译成中文）"""
        if not text:
            return ""
        try:
            ollama_util = OllamaUtil(model=model, current_language=current_language,
                                     target_language=target_language,
                                     ollama_host=ollama_host)
            translated = ollama_util.simple_translate(text)
            print(f"原文（{text}）")
            print(f"译文（{translated}）")
            return translated
        except Exception as e:
            print(f"翻译失败（{text}）：{e}")
            return text  # 翻译失败则返回原文

    def generate_srt(self, segments=None):
        srt_path = os.path.join(self.out_path, f"output_subtitle_{time.strftime('%Y%m%d%H%M%S')}.srt")
        """生成SRT字幕文件（包含原文+翻译）"""
        if segments is None:
            segments = []
        with open(srt_path, "w", encoding="utf-8") as f:
            for idx, seg in enumerate(segments, 1):
                # 转换时间戳格式
                start_time = format_timestamp(seg["start"])
                end_time = format_timestamp(seg["end"])

                # 翻译文本
                original_text = seg["text"]
                translated_text = self.translate_text(original_text)

                # 写入SRT格式（序号 → 时间范围 → 字幕内容）
                f.write(f"{idx}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{original_text}\n")
                f.write(f"{translated_text}\n\n")
        print(f"字幕文件生成完成：{srt_path}")
        return srt_path

if __name__ == '__main__':
    SpeechUtil.translate_text(text="世界那么大我想去看看", current_language="cn", target_language="en")