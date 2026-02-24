import requests
import chromadb
import uuid

# ===================== 1. 配置Ollama参数 =====================
OLLAMA_BASE_URL = "http://localhost:11434"
# 可选：嵌入模型（mokaai/m3e-base 做本地知识库时, 使用这个模型）
EMBEDDING_MODEL = "turingdance/m3e-base"
# 生成式LLM (不同的模型验证效果)
LLM_MODEL = "qwen3:4b"
LLM_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
LLM_MODEL = "granite4:3b"


# ===================== 2. 封装Ollama API调用函数 =====================
def get_embedding(text):
    """调用Ollama Embeddings API生成向量"""
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    data = {
        "model": EMBEDDING_MODEL,
        "prompt": text,
        "options": {"temperature": 0.0}  # 向量化无需随机性
    }
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()  # 抛出HTTP错误
        return response.json()["embedding"]
    except Exception as e:
        print(f"向量化失败：{e}")
        return None


def generate_answer(prompt):
    """调用 Ollama 的 OpenAI /v1/chat 接口生成回答"""
    url = f"{OLLAMA_BASE_URL}/v1/chat/completions"
    data = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "stream": False,
    }
    try:
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        choices = result.get("choices") or []
        if not choices:
            print(f"警告：模型未返回choices，原始响应: {result}")
            return ""
        message = choices[0].get("message") or {}
        answer = message.get("content", "").strip()
        if not answer:
            print(f"警告：模型返回空content，原始响应: {result}")
        return answer
    except requests.exceptions.Timeout:
        print("生成回答失败：请求超时，请检查模型是否已下载")
        return None
    except requests.exceptions.ConnectionError:
        print("生成回答失败：无法连接到Ollama服务")
        return None
    except Exception as e:
        print(f"生成回答失败：{e}")
        return None


def build_collection(texts):
    """根据传入的知识库文本创建临时向量库集合，并返回集合对象。"""
    client = chromadb.Client()
    # 使用随机名称，避免与已有集合冲突
    collection_name = f"kb_{uuid.uuid4().hex}"
    collection = client.create_collection(name=collection_name)

    embeddings = []
    valid_texts = []
    ids = []
    for idx, text in enumerate(texts):
        vec = get_embedding(text)
        if vec:
            embeddings.append(vec)
            valid_texts.append(text)
            ids.append(str(idx + 1))

    if not embeddings:
        print("知识库向量化失败：所有文本均向量化失败")
        return None

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=valid_texts,
    )
    print(f"知识库加载完成，共存入 {len(valid_texts)} 条数据")
    return collection


# ===================== 3. RAG核心流程：检索 + 生成 =====================
def rag_answer(question, texts):
    """完整RAG流程：问题向量化 → 检索相关文档 → 生成回答。

    参数：
        question: 用户问题字符串
        texts: 知识库文本列表，每个元素是一条文档
    """
    collection = build_collection(texts)
    if not collection:
        return "知识库构建失败，请检查向量化服务"

    # 步骤1：问题向量化
    q_vec = get_embedding(question)
    if not q_vec:
        return "问题向量化失败，请重试"

    # 步骤2：检索最相关的文档（取Top3）
    results = collection.query(
        query_embeddings=[q_vec],
        n_results=3,
    )
    docs = results.get("documents") or [[]]
    if not docs[0]:
        return "未检索到相关信息"

    # 将多条文档拼接为一个上下文
    context = "\n".join(docs[0])
    prompt = f"""请根据以下资料回答问题，仅使用资料中的信息，不要编造内容。
资料：
{context}
问题：{question}"""

    # 步骤3：调用LLM生成回答
    answer = generate_answer(prompt)
    return answer


# ===================== 5. 测试 =====================
if __name__ == "__main__":
    # 示例1: 知识库文本（可根据需要替换为任意知识库）
    kb_texts = [
        "2025年公司年终奖发放规则：全年绩效达标者发放3个月工资",
    ]
    user_question = "2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？"
    print(f"问题：{user_question}")
    answer = rag_answer(user_question, kb_texts)
    print(f"回答：{answer}")
    print("-" * 50)
    print("\r")

    # 示例2: 知识库文本（可根据需要替换为任意知识库）
    kb_texts = [
        "2025年公司年终奖发放规则：全年绩效达标者发放3个月工资",
        "2025年考勤规则：每月迟到超3次扣绩效，无年终奖",
        "2024年年终奖已发放完毕，标准为2个月工资",
    ]

    # 测试问题（可根据需要修改）
    user_question = "2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？"
    print(f"问题：{user_question}")
    answer = rag_answer(user_question, kb_texts)
    print(f"回答：{answer}")
    print("-" * 50)
    print("\r")

    # 示例3: 知识库文本（可根据需要替换为任意知识库）
    kb_texts = [
        "2024年年终奖已发放完毕，标准为2个月工资",
    ]

    # 测试问题（可根据需要修改）
    user_question = "2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？"
    print(f"问题：{user_question}")
    answer = rag_answer(user_question, kb_texts)
    print(f"回答：{answer}")
    print("-" * 50)
    print("\r")
