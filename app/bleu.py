import concurrent
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

import jieba
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from app.mysql.db_utils import get_db
from app.translation import generate


def blue_score(candidate, reference):
    # 分词
    candidate_fenci = ' '.join(jieba.cut(candidate))
    reference_fenci = ' '.join(jieba.cut(reference))
    candidate = candidate_fenci.split()
    reference = reference_fenci.split()
    smoother = SmoothingFunction()
    # 计算BLEU分数
    bleu_score = sentence_bleu([reference], candidate, smoothing_function=smoother.method1)
    return str(bleu_score)


# 线程追踪装饰器
def thread_tracker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread_id = threading.get_ident()
        print(f"线程 {thread_id} 开始处理任务")
        try:
            result = func(*args, **kwargs)
            print(f"线程 {thread_id} 完成任务")
            return result
        except Exception as e:
            print(f"线程 {thread_id} 处理失败: {str(e)}")
            raise
    return wrapper


def bleu_transl(sourceLang, targetLang, Text):
    generate(sourceLang, targetLang, Text)
    result = {
        'source': Text,
        'first': '',
        'reflect': '',
        'improve': ''
    }
    for chunk in generate(sourceLang, targetLang, Text):
        try:
            data = json.loads(chunk.strip().replace('data: ', ''))
            if data.get('stage') == 'first':
                result['first'] += data.get('chunk', '')
            elif data.get('stage') == 'reflect':
                result['reflect'] += data.get('chunk', '')
            elif data.get('stage') == 'improve':
                result['improve'] += data.get('chunk', '')
        except Exception as e:
            print(f"Error processing chunk: {e}")
    return result


@thread_tracker
def process_single_row(row):
    from test import app
    with app.app_context():
        db = get_db()
        try:
            chinese_text = row['chinese']
            reference_english = row['english']
            min_bleu = 0.2  # 设置最小BLEU阈值
            # 中译英（type=0）
            zh_en_result = bleu_transl('zh', 'en', chinese_text)
            zh_en_first_score = float(blue_score(zh_en_result['first'], reference_english))
            zh_en_improve_score = float(blue_score(zh_en_result['improve'], reference_english))
            if zh_en_first_score >= min_bleu and zh_en_improve_score >= min_bleu:
                # 存储中译英结果
                store_bleu_result(
                    db=db,
                    original=chinese_text,
                    reference=reference_english,
                    translated=zh_en_result['improve'],
                    improve_score=zh_en_improve_score,
                    first_score=zh_en_first_score,
                    trans_type=0
                )

            # 英译中（type=1）
            en_zh_result = bleu_transl('en', 'zh', reference_english)
            en_zh_first_score = float(blue_score(en_zh_result['first'], chinese_text))
            en_zh_improve_score = float(blue_score(en_zh_result['improve'], chinese_text))
            if en_zh_first_score >= min_bleu and en_zh_improve_score >= min_bleu:
                # 存储英译中结果
                store_bleu_result(
                    db=db,
                    original=reference_english,
                    reference=chinese_text,
                    translated=en_zh_result['improve'],
                    improve_score=en_zh_improve_score,
                    first_score=en_zh_first_score,
                    trans_type=1  # 1表示英译中
                )
            if zh_en_improve_score < min_bleu and en_zh_improve_score < min_bleu:
                cursor = db.cursor()
                try:
                    cursor.execute("DELETE FROM parallelcorpus WHERE id = %s", (row['id'],))
                    db.commit()
                    print(f"已删除低质量平行语料 ID: {row['id']}")
                except Exception as e:
                    print(f"删除语料失败: {e}")
                    db.rollback()
                finally:
                    cursor.close()
        finally:
            db.close()  # 确保关闭连接
    return row['id'], {
        'zh_en': {'first': zh_en_first_score, 'improve': zh_en_improve_score},
        'en_zh': {'first': en_zh_first_score, 'improve': en_zh_improve_score}
    }


def bleuScoreChart():
    """多线程批量处理平行语料"""
    from test import app
    with app.app_context():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            # 获取所有平行语料数据
            cursor.execute("SELECT id, chinese, english FROM parallelcorpus")
            results = cursor.fetchall()
            # 使用线程池处理
            with ThreadPoolExecutor(max_workers=8) as executor:
                # 提交所有任务
                futures = [
                    executor.submit(process_single_row, row)
                    for row in results
                ]
                # 等待所有任务完成并处理结果
                for future in concurrent.futures.as_completed(futures):
                    try:
                        task_id, score = future.result()
                        print(f"处理完成: ID {task_id}, 分数 {score}")
                    except Exception as e:
                        print(f"任务处理异常: {e}")

        except Exception as e:
            print(f"处理平行语料失败: {e}")
            db.rollback()
        finally:
            cursor.close()
            db.close()


def store_bleu_result(db, original, reference, translated, improve_score, first_score, trans_type):
    """存储BLEU评分结果到数据库"""
    cursor = db.cursor()
    try:
        cursor.execute("""
        INSERT INTO bleu_results 
        (original, reference, translated, improve_score, first_score, type)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (original, reference, translated, float(improve_score), float(first_score), trans_type))
        db.commit()
    except Exception as e:
        print(f"存储结果失败: {e}")
        db.rollback()
    finally:
        cursor.close()



