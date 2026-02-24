import os
import time

from openai import OpenAI
import httpx


class SyncChat:
    """同步聊天客户端类
    
    用于与本地Ollama服务进行同步聊天交互的客户端封装。
    主要功能：
    - 初始化OpenAI客户端连接本地Ollama服务
    - 提供流式聊天响应功能
    - 配置HTTP连接参数和超时设置
    - 处理模型推理过程中的reasoning和content内容
    """
    def __init__(self):
        self.client = OpenAI(
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
                    max_connections=100,
                    max_keepalive_connections=20,
                    keepalive_expiry=45.0,
                ),
                http1=True,  # 强制 HTTP/1.1，避免 HTTP/2 兼容问题
            ),
        )

    def sync_chat_stream(self):
        return self.client.chat.completions.create(
            model="qwen3:4b",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个得力的助手, 名字是PI, 出生在2030年11月1日",
                },
                {"role": "user", "content": "你的千问么?"},
            ],
            temperature=0.7,
            max_tokens=512,
            stream=True,
        )


if __name__ == "__main__":
    start_time = time.time()
    try:
        res = SyncChat().sync_chat_stream()
        for i in res:
            if not i.choices:
                continue
            delta = i.choices[0].delta
            # Ollama qwen3 等推理模型把内容放在 delta.reasoning，正文在 delta.content
            part = (delta.content or "") + (getattr(delta, "reasoning", None) or "")
            if part:
                print(part, end="")
        print()  # 结尾换行
    except Exception as e:
        print(f"请求失败: {e}")
    print(f"耗时: {time.time() - start_time:.2f}s")
