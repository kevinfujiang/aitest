# AI学习项目

这是一个用于学习和练习AI相关技术的项目，主要涉及大语言模型、函数调用、Agent代理等核心技术。

## 🚀 项目概述

本项目基于Python 3.12+开发，集成了多种AI框架和技术栈，包括OpenAI、LangChain、LangGraph等，旨在通过实践案例深入理解AI应用开发的核心概念。

## 🛠️ 技术栈

- **编程语言**: Python 3.12+
- **核心框架**: 
  - `openai` >= 2.17.0 - OpenAI API客户端
  - `langchain` >= 1.2.9 - LangChain框架
  - `langchain-openai` >= 1.1.8 - LangChain与OpenAI集成
  - `langgraph` >= 1.0.8 - 图形化工作流框架
  - `langgraph-supervisor` >= 0.0.31 - 多Agent协调框架
- **HTTP客户端**: `httpx` >= 0.28.1
- **向量数据库**: `chromadb` >= 1.5.1
- **嵌入模型**: `sentence-transformers` >= 5.2.3
- **构建工具**: Poetry
- **代码规范**: flake8 (最大行长度100字符)

## 📁 项目结构

```
test1/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── class_method_learn.py    # 类方法学习示例
│   ├── copy_learn.py           # 深浅拷贝学习
│   ├── debug_ollama.py         # Ollama调试工具
│   ├── deepseek.py             # DeepSeek模型调用示例
│   ├── function_learn.py       # 函数调用基础学习
│   ├── function_tool.py        # 带日志的函数工具实现
│   ├── multi_agent.py          # 多Agent协作示例
│   ├── single_agent.py         # 单Agent示例
│   └── rag/                    # RAG（检索增强生成）相关示例
│       └── rag_test.py         # 基于本地Ollama + ChromaDB 的RAG DEMO
├── .flake8                 # 代码规范配置
├── APPMOD_SETTINGS.md      # VS Code扩展配置说明
├── poetry.lock             # 依赖锁定文件
├── pyproject.toml          # 项目配置文件
└── README.md               # 项目说明文档
```

## 🔧 环境准备

### 1. 安装依赖

```bash
# 使用Poetry安装依赖
cd /Users/xuxiaorong/Code/demo/ai/test1
poetry install
```

### 2. 启动Ollama服务

本项目使用本地Ollama服务作为模型后端，请确保已安装并启动Ollama：

```bash
# 启动Ollama服务
ollama serve

# 拉取所需模型（根据需要选择）
ollama pull qwen3:4b
ollama pull llama3-groq-tool-use:8b
ollama pull phi4-mini:latest
```

### 3. 验证环境

```bash
# 测试Ollama连接
python src/debug_ollama.py
```

## ▶️ 运行示例

### 基础函数调用示例

```bash
# 运行基础函数调用学习
python src/function_learn.py
```

### 带日志的函数工具

```bash
# 运行带日志记录的函数工具
python src/function_tool.py
# 日志将输出到控制台和 function_tool.log 文件
```

### 单Agent示例

```bash
# 运行单Agent计算器
python src/single_agent.py
```

### 多Agent协作示例

```bash
# 运行多Agent协调器
python src/multi_agent.py
```

### 模型调用测试

```bash
# 测试DeepSeek模型调用
python src/deepseek.py
```

### RAG 知识库问答示例

```bash
# 基于本地Ollama + ChromaDB 的简易RAG示例
python src/rag/rag_test.py
```

## 📖 核心功能说明

### 1. 函数调用 (Function Calling)

- **function_learn.py**: 展示如何使用OpenAI的函数调用功能
- **function_tool.py**: 使用LangChain工具装饰器实现函数调用，并集成日志记录
- 支持的工具函数：
  - `get_weather(city)`: 获取城市天气（模拟）
  - `get_current_time()`: 获取当前时间
  - `computing_time(start_time, end_time)`: 计算时间差

### 2. Agent代理

- **single_agent.py**: 单个Agent实现基本数学运算
- **multi_agent.py**: 多Agent协作，包含时间代理和数学代理
- 使用LangChain的Agent框架和LangGraph的监督器模式

### 3. 模型交互

- **deepseek.py**: 展示如何与不同模型进行流式对话
- **debug_ollama.py**: Ollama服务连接调试工具

### 4. RAG（检索增强生成）

- **rag/rag_test.py**:
  - 使用 `chromadb` 作为本地向量数据库，按需构建临时集合
  - 通过 `/v1/chat/completions` 调用本地 Ollama（OpenAI 兼容接口）
  - 核心接口：`rag_answer(question, texts)`，其中：
    - `question`: 待提问的问题字符串
    - `texts`: 知识库文档列表（`list[str]`），方便在不同知识库场景下评估回答质量
  - 内部流程：问题向量化 → Top-K 文档检索（默认Top3）→ 将检索结果与问题一起构造成 prompt → 交给 LLM 生成回答

## ⚙️ 配置说明

### 模型配置

项目中的模型配置位于各文件中，可根据需要修改：

```python
# 示例模型配置
ollama_model = "qwen3:4b"  # 可替换为其他模型
base_url = "http://127.0.0.1:11434/v1"
api_key = "ollama"
```

### 日志配置

`function_tool.py` 中已配置日志系统：
- 输出级别：INFO
- 输出格式：时间戳 - 级别 - 消息
- 输出目标：控制台 + function_tool.log文件
- 编码：UTF-8

## 📝 开发规范

### 代码风格
- 遵循PEP 8规范
- 使用flake8进行代码检查（最大行长度100字符）
- 保持代码整洁，及时清理未使用的import

### 日志规范
- 关键操作必须添加日志记录
- 使用适当的日志级别（DEBUG/INFO/WARNING/ERROR）
- 日志消息应清晰描述操作内容和结果

## 🤝 学习资源

- [OpenAI官方文档](https://platform.openai.com/docs)
- [LangChain官方文档](https://python.langchain.com/)
- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [Ollama官方文档](https://github.com/ollama/ollama)

## 📄 许可证

MIT License

## 📧 联系方式

作者: xuxiaorong

---

*该项目主要用于AI技术学习和实践，欢迎提出改进建议！*
