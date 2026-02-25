"""基于 Milvus Lite 的 Markdown 知识库同步与检索问答（参考 sync_embedding.py）。"""

import os
import re
import sys
import types
from dataclasses import dataclass
from typing import List, Tuple

# Milvus Lite 依赖 pkg_resources，在 Python 3.12 等环境中可能不可用，用 importlib.metadata 兜底
if "pkg_resources" not in sys.modules:
    try:
        import pkg_resources  # noqa: F401  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        import importlib.metadata
        _pr = types.ModuleType("pkg_resources")
        _pr.DistributionNotFound = type("DistributionNotFound", (Exception,), {})
        def _get_distribution(name):
            try:
                return importlib.metadata.distribution(name)
            except importlib.metadata.PackageNotFoundError:
                raise _pr.DistributionNotFound()
        _pr.get_distribution = _get_distribution
        sys.modules["pkg_resources"] = _pr

import requests
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import ChatOpenAI
from pymilvus import MilvusClient


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "turingdance/m3e-base"
LLM_MODEL = "granite4:3b"
# m3e-base 常见向量维度，与 create_collection 的 dimension 一致
EMBEDDING_DIM = 768


@dataclass
class SimpleDoc:
    page_content: str
    metadata: dict


class SyncEmbeddingV2:
    """从 Markdown 同步向量到 Milvus Lite，并基于本地 Ollama 进行问答。"""

    def __init__(
        self,
        collection_name: str,
        db_path: str = "./my_local_milvus_kb.db",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        dimension: int = EMBEDDING_DIM,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.dimension = dimension
        self.collection_name = collection_name

        self.client = MilvusClient(db_path)
        self._ensure_collection()
        self._id_counter = self._next_id_start()

        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            base_url=f"{OLLAMA_BASE_URL}/v1",
        )

    def _ensure_collection(self) -> None:
        if not self.client.has_collection(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type="COSINE",
                enable_dynamic_field=True,
            )

    def _next_id_start(self) -> int:
        try:
            stats = self.client.get_collection_stats(self.collection_name)
            return int(stats.get("row_count", 0))
        except Exception:
            return 0

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
        """从 Markdown 文件载入知识库，切分、向量化并写入 Milvus Lite。返回写入的文档块数量。"""
        loader = UnstructuredMarkdownLoader(file_path)
        docs = loader.load()

        split_docs: List[SimpleDoc] = []
        for doc in docs:
            meta = doc.metadata or {}
            for chunk_text in self._chunk_text_semantic(doc.page_content):
                if chunk_text.strip():
                    split_docs.append(SimpleDoc(page_content=chunk_text, metadata=meta))

        if not split_docs:
            return 0

        base_name = os.path.basename(file_path)
        ids: List[int] = []
        rows: List[dict] = []
        for idx, doc in enumerate(split_docs, start=1):
            emb = self.embedding(doc.page_content)
            pk = self._id_counter + len(ids)
            doc_id = f"{base_name}_{idx}"
            ids.append(pk)
            rows.append({
                "id": pk,
                "vector": emb,
                "content": doc.page_content,
                "doc_id": doc_id,
            })
        self._id_counter += len(rows)

        self.client.insert(
            collection_name=self.collection_name,
            data=rows,
        )
        return len(rows)

    def query_vector(self, query: str, n_results: int = 3) -> Tuple[str, list]:
        """从向量库检索并用 LLM 生成答案。返回 (answer, raw_results)。"""
        query_emb = self.embedding(query)
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_emb],
            limit=n_results,
            output_fields=["content"],
            search_params={"metric_type": "COSINE"},
        )
        if not results or not results[0]:
            return "未检索到相关信息。", results

        hits = results[0]
        contents = []
        for h in hits:
            entity = h.get("entity") or {}
            text = entity.get("content")
            if text:
                contents.append(text)
        context = "\n".join(contents)

        prompt = f"""你是公司内部政策助手，请严格依据下列资料回答问题，只能使用资料中的信息，不要编造。

资料：
{context}

问题：{query}
"""
        llm_res = self.llm.invoke(prompt)
        answer = llm_res.content if hasattr(llm_res, "content") else str(llm_res)
        return answer, results

    def _chunk_text_semantic(self, text: str) -> List[str]:
        """按 Markdown 标题与段落边界切分，超长时再按长度与重叠切分。"""
        if not text.strip():
            return []

        header_pattern = re.compile(r"(?m)^(?=#{1,6}\s)", re.MULTILINE)
        sections = [s.strip() for s in header_pattern.split(text) if s.strip()]

        chunks: List[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            paragraphs = [p.strip() for p in section.split("\n\n") if p.strip()]
            current: List[str] = []
            current_len = 0
            for para in paragraphs:
                if current_len + len(para) + 2 <= self.chunk_size:
                    current.append(para)
                    current_len += len(para) + 2
                else:
                    if current:
                        chunks.append("\n\n".join(current))
                    if len(para) <= self.chunk_size:
                        current = [para]
                        current_len = len(para) + 2
                    else:
                        for sub in self._split_long_paragraph(para):
                            chunks.append(sub)
                        current = []
                        current_len = 0
            if current:
                chunks.append("\n\n".join(current))
        return chunks

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """将超长单段按句/行切分，再按 chunk_size 与 chunk_overlap 滑动。"""
        parts = re.split(r"(?<=[。！？.!?\n])", paragraph)
        parts = [p.strip() for p in parts if p.strip()]
        if not parts:
            parts = [paragraph]

        result: List[str] = []
        buf: List[str] = []
        buf_len = 0
        for p in parts:
            if buf_len + len(p) + 1 <= self.chunk_size:
                buf.append(p)
                buf_len += len(p) + 1
            else:
                if buf:
                    result.append("".join(buf))
                if len(p) > self.chunk_size:
                    step = max(1, self.chunk_size - self.chunk_overlap)
                    start = 0
                    while start < len(p):
                        result.append(p[start: start + self.chunk_size])
                        start += step
                    buf = []
                    buf_len = 0
                else:
                    buf = [p]
                    buf_len = len(p) + 1
        if buf:
            result.append("".join(buf))
        return result

    def ask_with_knowledge_base(self, kb_file_name: str, question: str) -> Tuple[int, str]:
        """给定知识库文件路径或名称，同步向量后对提问进行检索问答。返回 (写入的文档块数, 答案)。"""
        if not os.path.isabs(kb_file_name):
            kb_file_name = os.path.join(os.path.dirname(__file__), kb_file_name)
        inserted = self.insert_vector(kb_file_name)
        answer, _ = self.query_vector(question)
        return inserted, answer


if __name__ == "__main__":
    sync = SyncEmbeddingV2(collection_name="demo_markdown_kb")

    inserted, answer = sync.ask_with_knowledge_base(
        "ollama_api_format.md",
        "简要说明 Ollama /api/embeddings 接口的请求字段有哪些？",
    )
    print(f"已向量化并写入 Milvus Lite 的文档块数量：{inserted}")
    print("问题：简要说明 Ollama /api/embeddings 接口的请求字段有哪些？")
    print("回答：", answer)
    print("-" * 50)

    inserted, answer = sync.ask_with_knowledge_base(
        "知识库_考核要求.md",
        "2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？",
    )
    print(f"已向量化并写入 Milvus Lite 的文档块数量：{inserted}")
    print("问题：2025年公司的年终奖怎么发？5月份我有4次迟到,会影响年终奖吗？")
    print("回答：", answer)
    print("-" * 50)
