import requests
import json

url = "https://api.deepseek.com/v1/chat/completions"
api_key = "sk-47255ad3f9cd435b9375f213d6be59bd"  # <--- 粘贴你的新API Key

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}]
}

response = requests.post(url, headers=headers, json=payload)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("成功！返回内容：")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print("失败，返回内容：")
    print(response.text)