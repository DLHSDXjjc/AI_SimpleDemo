import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def extract_text_from_epub(epub_path):
    book = epub.read_epub(epub_path)
    text = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text.append(soup.get_text())
    return '\n'.join(text)

def clean_text(text):
    # 1. 将连续换行（2个及以上）替换成单个换行
    text = re.sub(r'\n{2,}', '\n', text)
    # 2. 将连续空格替换成一个空格
    text = re.sub(r' +', ' ', text)
    # 3. 去掉行首行尾空格
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    return text

# 转换《冰鉴》
bingjian_text = extract_text_from_epub('jiashu.epub')
bingjian_text = clean_text(bingjian_text)
with open('jiashu.txt', 'w', encoding='utf-8') as f:
    f.write(bingjian_text)
print('文件转换完成')

# 转换《家书》（如果有单独的 epub）
# jiahu_text = extract_text_from_epub('jiahu.epub')
# with open('jiahu.txt', 'w', encoding='utf-8') as f:
#     f.write(jiahu_text)
# print('家书转换完成')