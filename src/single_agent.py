import asyncio
from typing import Type

from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

ollama_model = "qwen3:4b"
llm = ChatOpenAI(base_url = "http://127.0.0.1:11434/v1", model_name=ollama_model, api_key="ollama", temperature=0)

class AddArgs(BaseModel):
    a : int = Field(...,description="第一个数")
    b : int = Field(...,description="第二个数")

class AddTool(BaseTool):
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
    a : int = Field(..., description="这是一个被减数")
    b : int = Field(..., description="这是一个减数")

class SubTool(BaseTool):
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


agent = create_agent(model=llm, tools=[AddTool(), SubTool()])

async def call_agent_1():
    print("call_agent_1")
    res = await agent.ainvoke({"messages":["请帮我计算一下123+10-4等于多少"]})
    print(res)

def call_agent_2():
    print("call_agent_2")
    res = agent.invoke({"messages":["请帮我计算一下123+10-4等于多少"]})
    print(res)


if __name__ == '__main__':
    asyncio.run(call_agent_1())
    call_agent_2()