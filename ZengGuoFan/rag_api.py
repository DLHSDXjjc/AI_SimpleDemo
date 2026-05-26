import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import requests
from typing import List, Optional

# ========== 配置 ==========
# sk-47255ad3f9cd435b9375f213d6be59bd
DEEPSEEK_API_KEY = "sk-47255ad3f9cd435b9375f213d6be59bd"  # 替换成你的 Key
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# ========== 初始化 ==========
app = FastAPI(title="曾国藩智囊团子 RAG API")

print("正在加载向量模型...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("模型加载完成！")

print("正在连接向量数据库...")
client = chromadb.PersistentClient(path="./vector_db")
collection = client.get_collection("zengguofan_books")
print(f"数据库连接成功，共 {collection.count()} 条记录")

# ========== 请求/响应模型 ==========
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    success: bool
    query: str
    answer: str
    sources: List[str]

# ========== 检索函数 ==========
def search(query: str, top_k: int = 3):
    results = collection.query(query_texts=[query], n_results=top_k)
    passages = []
    if results['documents'] and results['documents'][0]:
        for doc in results['documents'][0]:
            passages.append(doc)
    return passages

# ========== 调用 DeepSeek ==========
def call_deepseek(system_prompt: str, user_message: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    try:
        response = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"调用 DeepSeek 失败: {e}")
        return "AI 服务暂时不可用，请稍后再试。"

# ========== API 接口 ==========
@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """主接口：接收问题，返回 RAG 回答"""
    query = request.query
    top_k = request.top_k
    
    # 1. 检索相关原文
    passages = search(query, top_k)
    
    if not passages:
        return QueryResponse(
            success=False,
            query=query,
            answer="没有找到相关原文，请换个问题试试。",
            sources=[]
        )
    
    # 2. 构建提示词
    context = "\n\n---\n\n".join(passages)
    system_prompt = """你是曾国藩，基于《冰鉴》《曾国藩家书》的原文回答用户问题。

    要求：
    1. 必须引用原文
    2. 给出你的判断
    3. 最后用白话总结"""
    
    user_message = f"""【相关原文】
    {context}

    【用户问题】
    {query}

    请按上述要求回答。"""
    
    # 3. 调用大模型生成回答
    answer = call_deepseek(system_prompt, user_message)
    
    return QueryResponse(
        success=True,
        query=query,
        answer=answer,
        sources=passages
    )

# ========== 健康检查 ==========
@app.get("/health")
def health():
    return {"status": "ok", "total_passages": collection.count()}

# ========== 启动 ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)