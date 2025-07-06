from typing import Union

from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.envConfig import Config
import json
from app.mysql.db_utils import get_db
from app.nlp_utils import nlp_en, nlp_zh

client = OpenAI(
    api_key=Config.api_key,
    base_url=Config.base_url,
)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


def getTerms(source_lang: str, source_text: str):
    # 输入文本的有效性检查
    if not source_text or not isinstance(source_text, str):
        raise ValueError("输入文本无效")
    # 初始化可能术语列表
    possible_terms = []
    # 提取中文术语
    if source_lang == '中文':
        if not nlp_zh:
            raise ValueError("中文NLP模型未加载")
        doc = nlp_zh(source_text)
        # 提取名词和专有名词
        possible_terms = [
            token.text for token in doc
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and not token.is_punct
        ]
    # 提取英文术语
    elif source_lang == '英语':
        if not nlp_en:
            raise ValueError("英语NLP模型未加载")
        doc = nlp_en(source_text)
        possible_terms = [
            chunk.text for chunk in doc.noun_chunks
            if chunk.root.pos_ in ['NOUN', 'PROPN'] and not any(tok.is_stop or tok.is_punct for tok in chunk)
        ]

        # 通过大写词组和名词组合进一步增加提取的多词术语
        for token in doc:
            # 尝试结合大写的名词来匹配多词术语
            if token.pos_ in ['NOUN', 'PROPN'] and token.dep_ == 'compound':
                possible_terms.append(token.text)
    # 不支持其他语言
    else:
        raise ValueError(f"不支持的语言: {source_lang} (应为'中文'或'英语')")
    # 去重并输出提取的术语
    possible_terms = list(set(possible_terms))
    print("提取的术语:", possible_terms)
    # 使用数据库查询匹配术语
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 使用占位符动态生成查询
        placeholders = ','.join(['%s'] * len(possible_terms))
        query = ""

        # 根据语言选择查询字段
        if source_lang == '中文':
            query = f"""
                SELECT chinese, english 
                FROM terms 
                WHERE chinese IN ({placeholders})
            """
        else:
            query = f"""
                SELECT chinese, english 
                FROM terms 
                WHERE english IN ({placeholders})
            """

        # 执行查询
        cursor.execute(query, possible_terms)
        matched_terms = cursor.fetchall()

        # 构造结果并返回
        term_pairs = []
        for term in matched_terms:
            if source_lang == '中文':
                term_pairs.append({
                    'chinese': term['chinese'],
                    'english': term['english']
                })
            else:
                term_pairs.append({
                    'english': term['english'],
                    'chinese': term['chinese']
                })
        return term_pairs
    except Exception as e:
        print(f"数据库查询出错: {e}")
        return []
    finally:
        # 确保关闭数据库连接
        cursor.close()
        db.close()


# 调用大模型
def get_completion(
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        model: str = "qwen-plus",
        temperature: float = 0.3,
        json_mode: bool = False,
) -> Union[str, dict]:
    if json_mode:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=0.8,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            stream_options={"include_usage": False}
        )
        for chunk in response:
            print(chunk.model_dump_json())
    else:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=0.8,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            stream_options={"include_usage": True}
        )
        for chunk in response:
            if chunk.choices:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content


# 初次翻译
def first_translation(
        source_language: str, target_language: str, source_text: str
) -> str:
    system_message = f"你是一位水利领域的翻译专家，擅长将{source_language}精准地翻译成{target_language}。"
    user_prompt = f"请将以下文本从{source_language}翻译成{target_language}。仅提供翻译后的文本，不需要额外的解释或注释。原文如下：{source_text}。 "
    for translation_chunk in get_completion(prompt=user_prompt, system_message=system_message):
        yield translation_chunk


# 第一次反思改进
def first_reflect_translation(
        source_lang: str,
        target_lang: str,
        source_text: str,
        translation_first: str,
        back_translation_text: str
) -> str:
    system_message = f"""作为{source_lang}→{target_lang}水利双语专家，确保翻译的专业性和准确性。"""

    reflection_prompt = f"""
    [评估任务]
    分析源文本、初版翻译和反向翻译确保核心术语的正反向译法一致性，执行深度质量检查：

    [源文本]（{source_lang}）
    {source_text}

    [初版翻译]
    {translation_first}

    [反向翻译]
    {back_translation_text}

    [评估规范]
    1. 术语一致性检查
    - 核心水利术语是否正确
    - 专业表述是否匹配行业规范
    - 正反向翻译是否实现闭环验证

    2. 技术准确性验证
    - 防洪调度、水文测算等专业流程描述是否精准
    - 工程参数（流量/高程/压力值）是否完整转换
    - 法律性条款是否保留完整语义

    3. 逻辑连贯性分析
    - 技术文档特有的因果逻辑链是否保留
    - 工程方案论证结构是否完整再现
    - 专业领域特有的排比句式是否合理转换

    4. 单位符号处理
    - 国际单位制(SI)转换是否符合规范
    - 中外计量单位是否标注换算公式
    - 专业符号（如▽表示高程）是否正确保留

    5. 语言质量评估
    - 技术文档的客观中立语体是否维持
    - 复杂长句是否合理切分
    - 专业文本特有的被动语态处理是否得当

    [问题分级]
    - 严重：关键术语错误/数据失真/法律风险（需立即修改）
    - 中等：逻辑断裂/专业表述失准（需优先处理）
    - 轻微：语体不当/冗余表述（建议优化）

    [输出格式]
    ### 评估报告
    1. [问题等级] |[问题类型]
       - 问题描述：
       - 修改建议：
    """
    prompt = reflection_prompt.format(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        translation_first=translation_first,
    )
    for translation_chunk in get_completion(prompt, system_message=system_message):
        yield translation_chunk


def first_improve_translate(
        source_lang: str,
        target_lang: str,
        source_text: str,
        translation_first: str,
        reflection: str,
        term_pairs=None
) -> str:
    system_message = f"""您是中英双语水利工程领域专业翻译专家，具有以下核心能力：
    . 精通水利工程专业术语体系，必须优先使用提供的标准术语表（若存在）
    2. 精准识别翻译中的技术性错误
    3. 严格遵循审校规范执行修改
    4. 保持技术文档的专业严谨性"""
    term_hint = ""
    if term_pairs and len(term_pairs) > 0:
        term_hint = "\n[标准术语表]\n" + "\n".join(
            f"{pair['chinese']} → {pair['english']}"
            if source_lang == '中文' else
            f"{pair['english']} → {pair['chinese']}"
            for pair in term_pairs
        )
    prompt = f"""
    需根据专业审校意见改进{source_lang}→{target_lang}的技术文档翻译
    {term_hint}
    [源文本]（{source_lang}）
    {source_text}
    [当前翻译]（{target_lang}）
    {translation_first}
    [审校意见]
    {reflection}
    [修改要求]
    1. **致命错误修正**（必须修改）：
   - 技术术语错误
   - 数据/单位转换错误
   - 影响技术含义的语法错误
    2. 优化建议处理（仅当明显改进时采纳）：
       - 句式结构调整
       - 专业表达优化
    3. 保留要素：
       - 原文技术语义完整性
       - 已正确翻译的专业术语（保持中英对照格式）
       - 数字/公式/计量单位等专业符号
    4. 输出格式：仅返回最终翻译文本
    """
    for translation_chunk in get_completion(prompt, system_message=system_message):
        yield translation_chunk


def generate(source_language, target_language, source_text, termbases=False):
    term_pairs = []
    try:
        yield f"data: {json.dumps({'stage': 'source', 'chunk': source_text})}\n\n"

        # 阶段1: 初次翻译
        full_translation = []
        for chunk in first_translation(source_language, target_language, source_text):
            full_translation.append(chunk)
            event_data = {'stage': 'first', 'chunk': chunk, 'progress': len(full_translation)}
            yield f"data: {json.dumps(event_data)}\n\n"
        if termbases:
            term_pairs = getTerms(source_language, source_text)
            print(term_pairs)
        # 阶段2: 反思翻译
        full_translation_text = ''.join(full_translation)
        similarity, back_translation_text = back_translation_confidence_check(source_language, target_language,
                                                                                    source_text)
        if similarity <= 0.95:
            reflection_chunks = []
            for chunk in first_reflect_translation(source_language, target_language,
                                                   source_text, full_translation_text, back_translation_text):
                reflection_chunks.append(chunk)
                yield f"data: {json.dumps({'stage': 'reflect', 'chunk': chunk, 'progress': len(reflection_chunks)})}\n\n"

            # 阶段3: 改进翻译
            reflection_text = ''.join(reflection_chunks)
            improve_chunks = []
            for chunk in first_improve_translate(source_language, target_language,
                                                 source_text, full_translation_text, reflection_text, term_pairs):
                improve_chunks.append(chunk)
                yield f"data: {json.dumps({'stage': 'improve', 'chunk': chunk, 'progress': len(improve_chunks)})}\n\n"
        else:
            yield f"data: {json.dumps({'stage': 'improve', 'chunk': full_translation_text, 'progress': 1})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


def back_translation_confidence_check(
        source_lang: str,
        target_lang: str,
        source_text: str):
    n = source_lang
    source_lang = target_lang
    target_lang = n
    back_translation_text = ''.join([
        chunk for chunk in first_translation(target_lang, source_lang, source_text)
    ])
    # 计算余弦相似度
    embeddings = model.encode([source_text, back_translation_text])
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]
    return similarity, back_translation_text
