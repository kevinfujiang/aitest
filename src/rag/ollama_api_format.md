# Ollama vs OpenAI API 响应格式对比

## OpenAI API 响应格式
```json
{
  "id": "chatcmpl-123",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant", 
      "content": "这是回答内容"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## Ollama API 响应格式

### 1. /api/generate (文本生成)
```json
{
  "model": "qwen3:4b-instruct-2507-q4_K_M",
  "response": "这是回答内容",
  "done": true,
  "context": [1, 2, 3, ...],  // 可选的上下文token
  "total_duration": 123456789,
  "load_duration": 12345678,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 12345678,
  "eval_count": 20,
  "eval_duration": 123456789
}
```

### 2. /api/embeddings (向量嵌入)
```json
{
  "embedding": [0.123, -0.456, 0.789, ...]  // 通常是768或1024维向量
}
```

### 3. /api/chat (对话接口)
```json
{
  "model": "qwen3:4b-instruct-2507-q4_K_M",
  "message": {
    "role": "assistant",
    "content": "这是回答内容"
  },
  "done": true
}
```

## 关键差异总结

| 特性 | OpenAI | Ollama |
|------|--------|--------|
| 主要响应字段 | `choices[0].message.content` | `response` |
| 角色信息 | `choices[0].message.role` | `message.role` (chat接口) |
| 完成标识 | `choices[0].finish_reason` | `done` |
| 使用统计 | `usage` 对象 | `prompt_eval_count`, `eval_count` 等 |
| 上下文管理 | 自动管理 | `context` 字段手动管理 |

## 代码适配建议

当从OpenAI迁移到Ollama时，需要修改响应处理逻辑：

```python
# OpenAI方式
content = response.json()["choices"][0]["message"]["content"]

# Ollama方式 (generate接口)
content = response.json().get("response", "")

# Ollama方式 (chat接口)  
content = response.json()["message"]["content"]
```