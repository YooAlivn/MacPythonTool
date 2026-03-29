import os
import shutil
from datetime import timedelta


def format_timestamp(seconds):
    """将秒数转换为SRT字幕的时间格式（00:00:00,000）"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    ms = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def rm_file_or_dir(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
    return