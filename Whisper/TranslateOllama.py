import ollama


def simple_translate(text: str, model: str = "qwen3:8b") -> str:
    """
    最简单的翻译函数

    Args:
        text: 待翻译的英文文本
        model: Ollama 模型名称

    Returns:
        中文翻译结果
    """
    prompt = f"将以下英文翻译成中文，只输出译文：\n\n{text}"

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"翻译失败: {e}"


# 使用简洁版
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("简洁版使用示例")
    print("=" * 50)

    result = simple_translate("Hello, how are you today?")
    print(f"翻译结果: {result}")