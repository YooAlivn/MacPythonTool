import ollama


def simple_translate(text: str, model: str = "qwen3:8b", original_lang: str = "english", target_lang: str = "chinese") -> str:
    """
    最简单的翻译函数

    Args:
        text: 待翻译的英文文本
        model: Ollama 模型名称

    Returns:
        中文翻译结果
        :param text:
        :param target_lang:
        :param model:
        :param original_lang:
    """
    prompt = (f"You are a professional translator. Translate the following text from {original_lang} "
              f"to {target_lang}. Maintain the original meaning, tone, and format. Output ONLY the translation.：\n\n{text}")
    print(f"translator prompt is {prompt}")

    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"翻译失败: {e}"


def unload_model(model: str = "qwen3:8b"):
    ## 卸载模型（退出上下文）
    ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': 'exit'}],
        keep_alive=0  # ← 关键：立即从内存释放
    )


# 使用简洁版
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("简洁版使用示例")
    print("=" * 50)

    result = simple_translate("Hello, how are you today?", model="qwen3:8b")
    print(f"翻译结果: {result}")