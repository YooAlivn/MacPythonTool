#!/bin/bash

# 自动进入脚本所在目录
cd "$(dirname "$0")"

clear
echo "========================================"
echo "      视频翻译工具（带默认值）"
echo "========================================"
echo ""

# ======================================
# 输入5个参数（回车=默认值）
# ======================================
# read -p "1 翻译模型 (默认：translategemma:4b)：" param1
echo "1 翻译模型 (默认：translategemma:4b)"
param1="translategemma:4b"

# read -p "2 ffmpeg地址 (默认：/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg)：" param2
echo "2 ffmpeg地址 (默认：/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg)"
param2="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"

current_date=$(date "+%Y-%m")
# read -p "3 视频文件所在目录以及结果文件输出目录 (默认：/Users/alvin/MediaSource/Yutobe/${current_date})：" param3
echo "3 视频文件所在目录以及结果文件输出目录 (默认：/Users/alvin/MediaSource/Yutobe/${current_date})"
param3="/Users/alvin/MediaSource/Yutobe/${current_date}"

read -p "4 视频文件名称 (默认：hp_20260402221656_16_9_final)：" param4
param4=${param4:-"hp_20260402221656_16_9_final"}

read -p "5 是否带文字幕？[Y/N] 默认 Y：" param5
param5=${param5:-"Y"}



echo ""
echo "========================================"
echo "            【参数确认】"
echo "========================================"
echo "翻译模型：    $param1"
echo "ffmpeg地址：  $param2"
echo "视频目录：    $param3"
echo "视频文件名：   $param4"
echo "是否带英文字幕：$param5"
echo "========================================"
echo ""

# ======================================
# 确认执行
# ======================================
read -p "是否确认执行？[Y/N] 默认 Y：" confirm
confirm=${confirm:-"Y"}

if [[ "$confirm" != "Y" && "$confirm" != "y" ]]; then
    echo "已取消！"
    exit 1
fi

echo ""
echo "========================================"
echo "           正在执行 Python 脚本..."
echo "========================================"
echo ""

# ======================================
# ✅ 关键：执行 Python 并实时输出 print
# ======================================
/Users/alvin/Projects/media-venv/bin/python AudioToSrt.py "$param1" "$param2" "$param3" "$param4" "$param5"

echo ""
echo "========================================"
echo "              执行完成！"
echo "========================================"
echo ""

# 执行完不关闭，等待回车
read -p "按回车键退出..."