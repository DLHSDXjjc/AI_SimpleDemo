import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import shutil
import hashlib
from sentence_transformers import SentenceTransformer
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ========== 1. 加载向量模型 ==========
print("正在加载向量模型...")
# 你可以尝试换用以下中文优化模型（取消注释即可）：
# model = SentenceTransformer('shibing624/text2vec-base-chinese')
model = SentenceTransformer('all-MiniLM-L6-v2')
print("模型加载完成！")

# ========== 2. 清空旧数据库，创建新库 ==========
db_path = "./vector_db"
if os.path.exists(db_path):
    print(f"发现旧数据库，正在清空 {db_path}...")
    shutil.rmtree(db_path)
print("创建新的数据库...")
client = chromadb.PersistentClient(path=db_path)
collection = client.create_collection(name="zengguofan_books")

# ========== 3. 定义两个专用切分器 ==========
# 《冰鉴》使用较小的块（200字符），保留更多古文细节
bingjian_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)

# 《家书》使用常规块（300字符）
jiahu_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=40,
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]
)

# ========== 4. 处理《冰鉴》 ==========
print("处理《冰鉴》...")
with open('bingjian_clean.txt', 'r', encoding='utf-8') as f:
    bingjian_text = f.read()
bingjian_chunks = bingjian_splitter.split_text(bingjian_text)
print(f"  《冰鉴》切分为 {len(bingjian_chunks)} 段")

# ========== 5. 处理《家书》 ==========
print("处理《家书》...")
try:
    with open('jiashu_clean.txt', 'r', encoding='utf-8') as f:
        jiashu_text = f.read()
    jiashu_chunks = jiahu_splitter.split_text(jiashu_text)
    print(f"  《家书》切分为 {len(jiashu_chunks)} 段")
except FileNotFoundError:
    print("  《家书》文件不存在，跳过")
    jiashu_chunks = []

# ========== 6. 合并数据 ==========
all_chunks = bingjian_chunks + jiashu_chunks
all_metadatas = (
    [{"book": "冰鉴", "index": i} for i in range(len(bingjian_chunks))] +
    [{"book": "家书", "index": i} for i in range(len(jiashu_chunks))]
)
all_ids = [hashlib.md5(f"{meta['book']}_{meta['index']}".encode()).hexdigest() for meta in all_metadatas]

# ========== 7. 批量存入数据库 ==========
print(f"正在存入 {len(all_chunks)} 个段落...")
batch_size = 100
for i in range(0, len(all_chunks), batch_size):
    batch_chunks = all_chunks[i:i+batch_size]
    batch_ids = all_ids[i:i+batch_size]
    batch_metadatas = all_metadatas[i:i+batch_size]
    collection.add(ids=batch_ids, documents=batch_chunks, metadatas=batch_metadatas)
    print(f"  已存入 {len(batch_chunks)} 段，累计 {min(i+batch_size, len(all_chunks))}/{len(all_chunks)}")

print(f"✅ 成功！知识库共有 {collection.count()} 条记录")

# ========== 8. 测试检索 ==========
print("\n测试检索...")
test_query = "怎么看一个人眼神是否正直"
results = collection.query(query_texts=[test_query], n_results=3)
print(f"问题：{test_query}")
print("最相关的原文：")
for i, doc in enumerate(results['documents'][0]):
    print(f"  {i+1}. {doc[:100]}...")