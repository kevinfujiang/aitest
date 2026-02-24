import asyncio
from typing import Type

from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph_supervisor import create_supervisor

ollama_model = "qwen3:4b"
llm = ChatOpenAI(base_url = "http://127.0.0.1:11434/v1", model_name=ollama_model, api_key="ollama", temperature=0)

class AddArgs(BaseModel):
    """加法运算参数模型
    
    用于定义加法工具所需的参数结构。
    包含两个必填整数参数：第一个数(a)和第二个数(b)
    """
    a : int = Field(...,description="第一个数")
    b : int = Field(...,description="第二个数")

class AddTool(BaseTool):
    """加法计算工具类
    
    继承自BaseTool的基础加法运算工具。
    支持同步和异步两种调用方式，用于执行两个数字的加法运算。
    在多Agent环境中由数学代理使用。
    """
    name : str = "add"
    description : str = "这是一个计算两个数的和的方法"
    args_schema : Type[BaseModel] = AddArgs

    def _run(self, a:int, b:int):
        result = a + b
        print(f"同步调用: 正在计算{a} + {b}...")
        print(f"计算结果为: {result}")
        return a + b

    async def _arun(self, a:int, b:int):
        result = a - b
        print(f"异步调用: 正在计算{a} + {b}...")
        print(f"计算结果为: {result}")
        return a + b

class SubArgs(BaseModel):
    """减法运算参数模型
    
    用于定义减法工具所需的参数结构。
    包含两个必填整数参数：被减数(a)和减数(b)
    """
    a : int = Field(..., description="这是一个被减数")
    b : int = Field(..., description="这是一个减数")

class SubTool(BaseTool):
    """减法计算工具类
    
    继承自BaseTool的基础减法运算工具。
    支持同步和异步两种调用方式，用于执行两个数字的减法运算。
    在多Agent环境中由数学代理使用。
    """
    name : str = "sub"
    description : str = "这是一个计算两个数的差的方法"
    args_schema : Type[BaseModel] = SubArgs

    def _run(self, a:int, b:int):
        result = a + b
        print(f"同步调用:正在计算{a} - {b} = {result}")
        return result

    async def _arun(self, a:int, b:int):
        result = a - b
        print(f"异步调用:正在计算{a} - {b} = {result}")
        return result


class DatetimeTool(BaseTool):
    """时间获取工具类
    
    继承自BaseTool的时间工具，用于获取当前系统时间。
    支持同步和异步两种调用方式，返回格式化的当前时间字符串。
    在多Agent环境中由时间代理专门负责处理。
    """
    name: str = "get_current_time"
    description: str = "获取当前本地时间，格式为 YYYY-MM-DD HH:MM:SS。"
    args_schema: Type[BaseModel] = BaseModel

    def _run(self):
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"获取当前时间: {current_time}")
        return current_time

    async def _arun(self):
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"获取当前时间: {current_time}")
        return current_time


datetime_agent = create_agent(model=llm, tools=[DatetimeTool()], name="datetime_agent")
math_agent = create_agent(model=llm, tools=[AddTool(), SubTool()], name="math_agent")
supervisor = create_supervisor(model=llm, agents=[math_agent, datetime_agent], output_mode="full_history",
                               prompt="""
                               你是管理两个代理的主管: \n
                               - 时间代理 datetime: 将与时间相关的人物分配给此代理\n
                               - 数学代理 math: 将与数学计算相关的人物分配给此代理\n 
                               你需要先将用户的指令拆解成一个一个的子任务. 制定执行计划,再开始调用每个代理进行完成. \n
                               一次将工作分配给一个代理, 不要并行呼叫代理. \n 
                               不要自己做任何工作. \n
                               """).compile()


async def call_agent_1():
    print("call_agent_1")
    # TODO: 需要实现 supervisor 调用逻辑
    res = await math_agent.ainvoke({"messages":["请帮我计算一下123+10-4等于多少"]})
    print("TODO: 实现 supervisor 调用")

def call_agent_2():
    print("call_agent_2")
    # TODO: 需要实现 supervisor 调用逻辑
    res = math_agent.invoke({"messages":["请帮我计算一下123+10-4等于多少"]})
    print("TODO: 实现 supervisor 调用")


if __name__ == '__main__':
    # asyncio.run(call_agent_1())
    # call_agent_2()
    res = supervisor.invoke({"messages":["告诉我现在几点了?"]})