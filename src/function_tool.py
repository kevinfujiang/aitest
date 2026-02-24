"""带日志记录的函数工具模块

该模块使用LangChain框架实现函数调用，并集成了完整的日志记录系统。
相比function_learn.py，该模块具有更好的可观测性和错误处理能力。

主要功能：
- 使用@tool装饰器定义标准工具函数
- 集成logging模块进行详细的操作日志记录
- 支持INFO/DEBUG/ERROR等多个日志级别
- 实现完整的LangChain工具调用流程
- 提供详细的执行过程追踪和结果监控

特色功能：
- UTF-8编码的日志文件输出
- 控制台和文件双重日志记录
- 详细的工具执行过程监控
- 完善的异常处理和错误日志

使用场景：生产环境下的函数调用实现参考
"""

import random
import time
import logging
from datetime import datetime

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 配置日志
logging.basicConfig(

    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('function_tool.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@tool
def get_weather(city: str):
    """查询指定城市的天气（模拟）。"""
    logger.info(f"开始查询城市天气: {city}")
    temperature = random.randint(1, 30)
    result = f"城市{city}的天气是晴天, 温度是{temperature}度"
    logger.info(f"天气查询结果: {result}")
    return result


@tool
def get_current_time():
    """获取当前本地时间，格式为 YYYY-MM-DD HH:MM:SS。"""
    logger.info("开始获取当前时间")
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logger.info(f"当前时间: {current_time}")
    return current_time


def _parse_datetime(s: str):
    """解析时间字符串，支持 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。仅日期时按当天 00:00:00。"""
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {s!r}")


@tool
def computing_time(start_time: str, end_time: str):
    """计算两个时间的秒数差。支持格式: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。"""
    logger.info(f"开始计算时间差: {start_time} 到 {end_time}")
    try:
        start_dt = _parse_datetime(start_time)
        end_dt = _parse_datetime(end_time)
        logger.debug(f"解析后的时间: 开始={start_dt}, 结束={end_dt}")
    except ValueError as e:
        error_msg = (
            f"参数格式错误，支持: YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD。"
            f"例如: 2026-02-10 11:00:00 或 2026-02-10。错误: {e}"
        )
        logger.error(error_msg)
        return error_msg
    delta = end_dt - start_dt
    result = delta.total_seconds()
    logger.info(f"时间差计算结果: {result} 秒")
    return result


tool_map = {
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "computing_time": computing_time,
}

# ollama_model = "functiongemma:latest"
# ollama_model = "llama3-groq-tool-use:8b"
# ollama_model = "phi4-mini:latest"
ollama_model = "qwen3:4b"
# ollama_model = "granite4:3b"

last_result = {}

llm = ChatOpenAI(
    model=ollama_model,
    temperature=0,
    api_key="ollama",
    base_url="http://127.0.0.1:11434/v1",
)
with_tool_llm = llm.bind_tools([get_current_time, get_weather, computing_time])
messages = [
    {
        "role": "system",
        "content": "你是一个专业的时间记录者, 涉及到时间和日期的,必须调用工具进行回答",
    },
    {
        "role": "user",
        "content": "请告诉我现在几点钟, 并告诉我和1980年1月1日相差多少天, 还有上海和北京的天气怎么样?",
    },
]

start_time = time.time()
logger.info("开始执行对话流程")

while True:
    logger.debug("调用 LLM 模型")
    res = with_tool_llm.invoke(messages)
    
    if res.tool_calls:
        logger.info(f"检测到 {len(res.tool_calls)} 个工具调用")
        messages.append(res)
        
        for tool_call in res.tool_calls:
            function_name = tool_call.get("name", None)
            args = tool_call.get("args") or {}
            tool_call_id = tool_call.get("id", "")
            
            logger.info(f"执行工具调用: {function_name}, 参数: {args}")
            
            if function_name in tool_map:
                tool_obj = tool_map[function_name]
                func_result = tool_obj.invoke(args)
                logger.info(f"工具执行结果: {func_result}")
                
                messages.append(
                    ToolMessage(
                        content=str(func_result),
                        tool_call_id=tool_call_id,
                    )
                )
            else:
                logger.warning(f"未知的工具名称: {function_name}")
                messages.append(
                    ToolMessage(
                        content=f"未知工具: {function_name}",
                        tool_call_id=tool_call_id,
                    )
                )
    else:
        logger.info("LLM 返回最终答案")
        messages.append(AIMessage(content=res.content))
        logger.info(f"最终回答: {res.content}")
        break

end_time = time.time()
elapsed_time = end_time - start_time
logger.info(f"对话流程完成，总耗时: {elapsed_time:.2f} 秒")
print(f"time: {elapsed_time} seconds")
print(messages)
