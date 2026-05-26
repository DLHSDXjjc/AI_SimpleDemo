import re

def clean_text(text):
    """清洗文本：只保留中文、常用标点、数字、字母"""
    # 1. 去掉不可见字符（包括 \x00 等）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # 2. 将连续换行替换成单个换行
    text = re.sub(r'\n+', '\n', text)
    
    # 3. 将连续空格替换成一个空格
    text = re.sub(r' +', ' ', text)
    
    # 4. 去掉行首行尾空格
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # 5. 去掉空行
    text = re.sub(r'\n+', '\n', text)
    
    return text

def clean_file(input_path, output_path):
    """读取原文件，清洗后保存"""
    # 尝试不同编码读取
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
    content = None
    for enc in encodings:
        try:
            with open(input_path, 'r', encoding=enc) as f:
                content = f.read()
            print(f"  ✅ 读取成功，编码: {enc}")
            break
        except Exception as e:
            print(f"  ❌ {enc} 失败: {e}")
    
    if content is None:
        print(f"  ❌ 无法读取 {input_path}")
        return False
    
    # 清洗内容
    cleaned = clean_text(content)
    
    # 保存为 UTF-8
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"  ✅ 清洗完成，保存为 {output_path}")
    print(f"     原大小: {len(content)} 字符 → 清洗后: {len(cleaned)} 字符")
    return True

# 清洗《冰鉴》
print("\n清洗《冰鉴》...")
clean_file('ZengGuoFan/bingjian.txt', 'ZengGuoFan/bingjian_clean.txt')

# 清洗《家书》
print("\n清洗《家书》...")
clean_file('ZengGuoFan/jiashu.txt', 'ZengGuoFan/jiashu_clean.txt')

print("\n✅ 全部完成！")