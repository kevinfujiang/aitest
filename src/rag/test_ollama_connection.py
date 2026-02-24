import requests
import json

def test_ollama_connection():
    """测试Ollama服务连接"""
    
    # 测试1: 检查Ollama是否运行
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务运行正常")
            models = response.json()
            print(f"已安装的模型: {[model['name'] for model in models.get('models', [])]}")
        else:
            print(f"❌ Ollama服务返回状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务，请确保:")
        print("   1. Ollama服务已启动 (运行: ollama serve)")
        print("   2. 端口11434未被占用")
        print("   3. 防火墙未阻止连接")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False
    
    # 测试2: 测试嵌入API
    try:
        embedding_data = {
            "model": "turingdance/m3e-base",
            "prompt": "测试文本"
        }
        response = requests.post(
            "http://localhost:11434/api/embeddings", 
            json=embedding_data, 
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print(f"✅ 嵌入API测试成功，向量维度: {len(embedding)}")
        else:
            print(f"❌ 嵌入API测试失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 嵌入API测试异常: {e}")
    
    # 测试3: 测试生成API
    try:
        generate_data = {
            "model": "granite4:3b",
            "prompt": "你好",
            "stream": False
        }
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json=generate_data, 
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"✅ 生成API测试成功，响应长度: {len(response_text)} 字符")
            if response_text:
                print(f"响应预览: {response_text[:100]}...")
        else:
            print(f"❌ 生成API测试失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 生成API测试异常: {e}")
    
    return True

if __name__ == "__main__":
    print("🔍 开始测试Ollama连接...")
    print("=" * 50)
    test_ollama_connection()
    print("=" * 50)
    print("测试完成")