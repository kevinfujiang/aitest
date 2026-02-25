import os
from dataclasses import dataclass
from typing import List, Tuple

import chromadb
import requests
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import ChatOpenAI


OLLAMA_BASE_URL = "http://127.0.0.1:11434"  # 本地Ollama地址
EMBEDDING_MODEL = "turingdance/m3e-base"  # 本地Ollama的嵌入模型,用于向量化文本
LLM_MODEL = "granite4:3b"  # 本地Ollama的LLM模型,用于生成答案


@dataclass
class SimpleDoc:
    page_content: str
    metadata: dict


class SyncEmbedding:
    """从 Markdown 同步向量到 Chroma，并基于本地 Ollama 进行问答。"""

    def __init__(self, collection_name: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        # 切分参数
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 本地 Chroma 向量库
        self.chroma_client = chromadb.PersistentClient(path="./my_local_chroma_kb")
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

        # 本地 Ollama LLM（OpenAI 兼容接口）
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            base_url=f"{OLLAMA_BASE_URL}/v1",
        )

    def embedding(self, text: str) -> List[float]:
        """使用本地 Ollama 的 turingdance/m3e-base 生成向量。"""
        url = f"{OLLAMA_BASE_URL}/api/embeddings"
        payload = {
            "model": EMBEDDING_MODEL,
            "prompt": text,
            "options": {"temperature": 0.0},
        }
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["embedding"]

    def insert_vector(self, file_path: str) -> int:
        """从 Markdown 文件载入知识库，切分、向量化并写入 Chroma。

        返回写入的文档块数量。
        """
        loader = UnstructuredMarkdownLoader(file_path)
        docs = loader.load()

        # 手动切分文档为小段，避免依赖额外的切分器包
        split_docs: List[SimpleDoc] = []
        for doc in docs:
            text = doc.page_content
            meta = doc.metadata or {}
            length = len(text)
            step = (
                self.chunk_size - self.chunk_overlap
                if self.chunk_size > self.chunk_overlap
                else self.chunk_size
            )
            start = 0
            while start < length:
                end = start + self.chunk_size
                chunk = text[start:end]
                if chunk.strip():
                    split_docs.append(SimpleDoc(page_content=chunk, metadata=meta))
                start += step

        ids: List[str] = []
        embeddings: List[List[float]] = []
        contents: List[str] = []
        metadatas: List[dict] = []

        for idx, doc in enumerate(split_docs, start=1):
            emb = self.embedding(doc.page_content)
            ids.append(str(idx))
            embeddings.append(emb)
            contents.append(doc.page_content)
            metadatas.append(doc.metadata)

        if not ids:
            return 0

        # 使用「文件名 + 序号」作为唯一 id，避免多次 insert 不同文件时 id 冲突导致后写入的文档无法入库
        base_name = os.path.basename(file_path)
        unique_ids = [f"{base_name}_{i}" for i in ids]

        self.collection.add(
            ids=unique_ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
        )
        return len(ids)

    def query_vector(self, query: str, n_results: int = 3) -> Tuple[str, dict]:
        """从向量库检索并用 LLM 生成答案。

        返回 (answer, raw_results)。
        """
        query_emb = self.embedding(query)
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=n_results,
        )

        docs = results.get("documents") or [[]]
        if not docs[0]:
            return "未检索到相关信息。", results

        context = "\n".join(docs[0])
        prompt = f"""你是公司内部政策助手，请严格依据下列资料回答问题，只能使用资料中的信息，不要编造。

资料：
{context}

问题：{query}
"""
        llm_res = self.llm.invoke(prompt)
        answer = llm_res.content if hasattr(llm_res, "content") else str(llm_res)
        return answer, results

    def ask_with_knowledge_base(self, kb_file_name: str, question: str) -> Tuple[int, str]:
        """给定知识库文件路径或名称，同步向量后对提问进行检索问答。

        若 kb_file_name 非绝对路径，则相对于本脚本所在目录解析。
        返回 (写入的文档块数, 答案)。
        """
        if not os.path.isabs(kb_file_name):
            kb_file_name = os.path.join(os.path.dirname(__file__), kb_file_name)
        inserted = self.insert_vector(kb_file_name)
        answer, _ = self.query_vector(question)
        return inserted, answer


if __name__ == "__main__":
    sync = SyncEmbedding(collection_name="demo_markdown_kb")

    inserted, answer = sync.ask_with_knowledge_base(
        "ollama_api_format.md",
        "简要说明 Ollama /api/embeddings 接口的请求字段有哪些？",
    )
    print(f"已向量化并写入 Chroma 的文档块数量：{inserted}")
    print("问题：简要说明 Ollama /api/embeddings 接口的请求字段有哪些？")
    print("回答：", answer)
    print("-" * 50)

    inserted, answer = sync.ask_with_knowledge_base(
        "知识库_考核要求.md",
        "2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？",
    )
    print(f"已向量化并写入 Chroma 的文档块数量：{inserted}")
    print("问题：2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？")
    print("回答：", answer)
    print("-" * 50)
