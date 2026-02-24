from openai import OpenAI
import httpx

# 连接本地的Ollama服务.

# 创建自定义 httpx Client（兼容旧版）
client = OpenAI(
    base_url="http://127.0.0.1:11434/v1",
    api_key="ollama",
    http_client=httpx.Client(
        timeout=httpx.Timeout(
            connect=10.0,  # 连接超时 10 秒
            read=60.0,  # 读取超时 60 秒
            write=60.0,
            pool=60.0,
        ),
        limits=httpx.Limits(
            max_connections=100, max_keepalive_connections=20, keepalive_expiry=45.0
        ),
        http1=True,  # 强制 HTTP/1.1，避免 HTTP/2 兼容问题
    ),
)

# 下面保持原样测试 models.list()
try:
    models = client.models.list()
    print("成功列出模型：")
    for m in models.data:
        print(f"- {m.id}")
except Exception as e:
    print("列模型失败:", str(e))
