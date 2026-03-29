import ollama
import requests

trans_key = {
    "en": "english",
    "zh": "chinese",
}


class OllamaUtil:
    def __init__(self, model: str = "qwen3:8b", current_language: str = "en", target_language: str = "zh",
                 ollama_host: str = "localhost"):
        self.client = ollama.Client(host=f"http://{ollama_host}:11434")
        self.model = model
        self.current_language = current_language
        self.target_language = target_language

    def simple_translate(self, text: str) -> str:
        prompt = (f"You are a professional translator. Translate the following text "
                  f"from {trans_key.get(self.current_language)} "
                  f"to {trans_key.get(self.target_language)}. "
                  f"Maintain the original meaning, tone, and format. Output ONLY the translation.：\n\n{text}")

        try:
            response = self.client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"翻译失败: {e}"

    def is_model_loaded(self):
        try:
            # 调用 Ollama 的 /api/ps 接口获取正在运行的模型列表 [citation:6][citation:10]
            response = self.client.ps()
            running_models = response.get("models")

            # 检查目标模型是否在列表中
            for model in running_models:
                if model.get("name") == self.model:
                    return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"API 请求失败: {e}")
            return False

    def unload_model(self):
        """
            卸载某个模型

            Args:
                model: Ollama 模型名称
            """
        ## 卸载模型（退出上下文）
        self.client.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': 'exit'}],
            keep_alive=0  # ← 关键：立即从内存释放
        )


# 使用简洁版
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("简洁版使用示例")
    print("=" * 50)
    ollama_util = OllamaUtil(model="translategemma:4b", current_language="en", target_language="zh",
                             ollama_host="192.168.7.110")
    result = ollama_util.simple_translate("Hello, how are you today?")
    print(f"翻译结果: {result}")
    ollama_util.unload_model()
