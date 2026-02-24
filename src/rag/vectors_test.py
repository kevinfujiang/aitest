import requests
import json

# 确保Ollama已启动并运行
# ollama pull turingdance/m3e-base

# 调用Ollama的m3e-base API生成向量
def get_m3e_embedding(text):
    url = "http://localhost:11434/api/embeddings"
    data = {
        "model": "turingdance/m3e-base",
        "prompt": text
    }
    response = requests.post(url, json=data)
    result = json.loads(response.text)
    return result["embedding"]  # 返回768维向量

# 测试
text = "2025年公司年终奖发放规则"
vector = get_m3e_embedding(text)
print("向量维度：", len(vector))  # 输出 768，符合预期
print("向量内容：", vector)
