import re
from docx import Document
import csv


def contains_english(text):
    """检查字符串是否包含至少一个英文字母"""
    return bool(re.search(r'[a-zA-Z]', text))


def docx_to_csv(input_file, output_file):
    doc = Document(input_file)
    entries = []
    current_entry = None
    in_notes = False

    # 正则匹配规则
    title_pattern = re.compile(r'^\d+(\.\d+)*\s+[\u4e00-\u9fff]+')  # 排除标题行
    entry_number_pattern = re.compile(r'^(\d+\.){2,}\d+$')  # 匹配有效编号

    for para in doc.paragraphs:
        text = para.text.strip()

        # 排除标题行（如 "2 陆地水文"）
        if title_pattern.match(text):
            continue

        # 检测新条目编号（如 "11.5.24"）
        if entry_number_pattern.match(text):
            if current_entry:
                # 保存当前条目的所有有效术语对为独立行（过滤不含英语的行）
                for cn, en in current_entry['术语对']:
                    if contains_english(en):  # 关键过滤逻辑
                        entries.append({
                            '编号': current_entry['编号'],
                            '中文': cn,
                            '英语': en,
                            '定义': ' '.join(current_entry['定义']).strip(),
                            '注释': '；'.join(current_entry['注释']).strip()
                        })
            # 初始化新条目
            current_entry = {
                '编号': text,
                '术语对': [],
                '定义': [],
                '注释': []
            }
            in_notes = False
            continue

        # 处理中英文术语行（支持同一段落多个术语）-----------------------------
        if current_entry and not current_entry['术语对']:
            pairs = []
            cn_buffer = []
            en_buffer = []
            in_en = False  # 标记是否正在收集英文术语

            for char in text:
                # 中文字符处理：开始新术语对
                if re.match(r'[\u4e00-\u9fff]', char):
                    if in_en:
                        # 遇到中文，保存当前术语对
                        if cn_buffer and en_buffer:
                            pairs.append((
                                ''.join(cn_buffer).strip(),
                                ' '.join(''.join(en_buffer).split())
                            ))
                            cn_buffer, en_buffer = [], []
                        in_en = False
                    cn_buffer.append(char)
                else:
                    # 非中文字符处理
                    if cn_buffer:
                        # 中文已存在，开始收集英文（跳过中英文之间的首空格）
                        if not in_en and char == ' ':
                            continue  # 跳过中英文之间的分隔空格
                        in_en = True
                        en_buffer.append(char)
            # 处理最后一个术语对
            if cn_buffer and en_buffer:
                pairs.append((
                    ''.join(cn_buffer).strip(),
                    ' '.join(''.join(en_buffer).split())
                ))
            if pairs:
                current_entry['术语对'] = pairs
                continue

        # 处理注释段落（以"注"开头）-----------------------------------------
        if current_entry and re.match(r'^注\d*：?', text):
            in_notes = True
            current_entry['注释'].append(text)
            continue

        # 收集定义或注释内容----------------------------------------------
        if current_entry:
            if in_notes:
                current_entry['注释'].append(text)
            else:
                current_entry['定义'].append(text)

    # 处理最后一个条目（同样需要过滤）
    if current_entry:
        for cn, en in current_entry['术语对']:
            if contains_english(en):  # 关键过滤逻辑
                entries.append({
                    '编号': current_entry['编号'],
                    '中文': cn,
                    '英语': en,
                    '定义': ' '.join(current_entry['定义']).strip(),
                    '注释': '；'.join(current_entry['注释']).strip()
                })

    # 写入CSV文件
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['编号', '中文', '英语', '定义', '注释'])
        for entry in entries:
            # 自动处理特殊字符（逗号、分号、换行）
            definition = f'"{entry["定义"]}"' if any(c in entry["定义"] for c in ',;"\n') else entry["定义"]
            notes = f'"{entry["注释"]}"' if any(c in entry["注释"] for c in ',;"\n') else entry["注释"]
            writer.writerow([entry['编号'], entry['中文'], entry['英语'], definition, notes])


# 使用示例
docx_to_csv('/水利01.docx', './resources/output.csv')
