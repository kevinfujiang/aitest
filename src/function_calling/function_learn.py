import time
import random
from datetime import datetime
from openai import OpenAI
import httpx
import json

"""函数调用基础学习模块

该模块演示了如何使用OpenAI的函数调用功能，实现与大语言模型的工具交互。

主要功能：
- 定义多个实用工具函数（天气查询、时间获取、时间计算）
- 配置OpenAI函数调用参数
- 实现完整的函数调用循环流程
- 处理模型的工具调用请求和结果返回
- 支持时间参数的智能补全功能

使用场景：学习OpenAI函数调用机制的基础示例
"""
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名称"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "computing_time",
            "description": "计算两个时间之间的秒数差, 秒可以转换成天数、小时数、分钟数、秒数.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "开始时间，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD"},
                    "end_time": {"type": "string", "description": "结束时间，格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD"},
                },
                "required": ["start_time", "end_time"],
            },
        },
    },
]


def get_weather(city: str):
    temperature = random.randint(10, 30)
    return f"城市{city}的天气是晴天, 温度是{temperature}度"


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _parse_datetime(s: str):
    """解析时间字符串，支持 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。仅日期时按当天 00:00:00。"""
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {s!r}")


def computing_time(start_time: str, end_time: str):
    """计算两个时间的秒数差。支持格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。"""
    try:
        start_dt = _parse_datetime(start_time)
        end_dt = _parse_datetime(end_time)
    except ValueError as e:
        return (
            f"参数格式错误，支持: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。"
            f"例如: 2026-02-10 11:00:00 或 2026-02-10。错误: {e}"
        )
    delta = end_dt - start_dt
    return delta.total_seconds()


tool_map = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "computing_time": computing_time,
}

messages = [
    {
        "role": "system",
        "content": "你是一个专业的时间记录者, 涉及到时间和日期的,必须调用工具进行回答",
    },
    {"role": "user", "content": "请告诉我现在几点钟, 并告诉我和1980年1月1日相差多少天"},
]


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
            max_connections=100,
            max_keepalive_connections=20,
            keepalive_expiry=45.0
        ),
        http1=True,  # 强制 HTTP/1.1，避免 HTTP/2 兼容问题
    ),
)

ollama_model = "qwen3:4b"
# ollama_model = "llama3-groq-tool-use:8b"
# ollama_model = "phi4-mini:latest"

last_result = {}
while True:
    res = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=False,
    )

    if res.choices[0].message.tool_calls:
        print("---> 1")
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": res.choices[0].message.tool_calls,
            }
        )
        for tool_call in res.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments or "{}")
            # 若调用 computing_time 且模型只传了 start_time，用上一轮 get_current_time 的 end_time 补全
            if tool_name == "computing_time" and "end_time" not in tool_args and "end_time" in last_result:
                tool_args["end_time"] = last_result["end_time"]
            try:
                tool_result = tool_map[tool_name](**tool_args)
                last_result["end_time"] = tool_result
            except TypeError as e:
                if "computing_time" in tool_name:
                    tool_result = (
                        "调用 computing_time 必须同时传入 start_time 和 end_time，"
                        "格式均为 YYYY-MM-DD HH:MM:SS。请先调用 get_current_time 获取当前时间再计算。"
                    )
                else:
                    tool_result = f"调用失败，参数不完整: {e}"
            print("---> 2")
            print(f"call --> tool: {tool_name}, args: {tool_args}, result: {tool_result}")
            messages.append(
                {
                    "role": "tool",
                    "content": str(tool_result),
                    "tool_call_id": tool_call.id,
                }
            )
    else:
        print("---> 3")
        messages.append(
            {"role": "assistant", "content": res.choices[0].message.content}
        )
        print(messages)
        break

print("---> 4")
