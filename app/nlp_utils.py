import spacy
import sys

try:
    print("正在加载英文模型...", file=sys.stderr)
    nlp_en = spacy.load("en_core_web_sm") if spacy.util.is_package("en_core_web_sm") else None
    print("英文模型加载状态:", "成功" if nlp_en else "失败", file=sys.stderr)

    print("正在加载中文模型...", file=sys.stderr)
    nlp_zh = spacy.load("zh_core_web_sm") if spacy.util.is_package("zh_core_web_sm") else None
    print("中文模型加载状态:", "成功" if nlp_zh else "失败", file=sys.stderr)
except Exception as e:
    print(f"模型加载异常: {str(e)}", file=sys.stderr)
    raise
