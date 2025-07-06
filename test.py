import jieba
from flask import Flask, request, stream_with_context, Response, send_from_directory
from app.bleu import blue_score, bleuScoreChart
from app.image_transl import image_text, translate_word

from app.envConfig import Config
from app.mysql.db_utils import get_db
from app.translation import generate, getTerms

jieba.initialize()
app = Flask(__name__)
app.config.from_object(Config)


@app.route('/imgTransl', methods=['POST'])
def imgTransl():
    data = request.json  # 获取 JSON 数据
    source_language = data.get('sourceLanguage', '')
    target_language = data.get('targetLanguage', '')
    img_path = data.get('imgPath', '')
    source_text = image_text(img_path)

    return Response(
        stream_with_context(generate(source_language, target_language, source_text)),
        mimetype='text/event-stream',
    )


@app.route('/getTerms', methods=['POST'])
def get_terms():
    data = request.json
    required_fields = ['sourceLanguage', 'sourceText']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return {'error': f'缺少必填字段: {", ".join(missing)}'}, 400
    try:
        source_lang = data['sourceLanguage']
        source_text = data['sourceText']
        term_pairs = getTerms(source_lang, source_text)
        return {
            'status': 'success',
            'data': term_pairs
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }, 500


@app.route('/wordTransl', methods=['POST'])
def wordTransl():
    data = request.json
    source_language = data.get('sourceLanguage', '')
    target_language = data.get('targetLanguage', '')
    word_path = data.get('imgPath', '')
    try:
        output_name = translate_word(source_language, target_language, word_path)
        return output_name
    except Exception as e:
        return str(e), 500


@app.route('/bleuscore', methods=['GET'])
def blueScore():
    candidate = request.args.get('candidate', '')
    reference = request.args.get('reference', '')
    return blue_score(candidate, reference)


@app.route('/translation', methods=['POST'])
def translation():
    data = request.json  # 获取 JSON 数据
    required_fields = ['sourceLanguage', 'targetLanguage', 'sourceText']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return {'error': f'Missing fields: {", ".join(missing)}'}, 400
    source_language = data.get('sourceLanguage', '')  # 从 JSON 数据中获取 sourceLanguage
    target_language = data.get('targetLanguage', '')  # 从 JSON 数据中获取 targetLanguage
    source_text = data.get('sourceText', '')  # 从 JSON 数据中获取 sourceText
    termbases = data.get('termbases', False)
    print(termbases)
    return Response(
        stream_with_context(generate(source_language, target_language, source_text, termbases)),
        mimetype='text/event-stream',
    )


@app.route('/getChart', methods=['GET'])
def getChart():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
               CREATE TABLE IF NOT EXISTS bleu_results (
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   original TEXT NOT NULL,
                   reference TEXT NOT NULL ,
                   translated TEXT NOT NULL,
                   improve_score FLOAT NOT NULL ,
                   first_score FLOAT NOT NULL ,
                   type TINYINT NOT NULL,
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
               """)
        db.commit()
        # 清空结果表
        cursor.execute("TRUNCATE TABLE bleu_results")
        db.commit()
        # 执行评分计算
        bleuScoreChart()
        return {
            'status': 'success',
            'message': 'BLEU评分计算已完成'
        }, 200
    except Exception as e:
        db.rollback()  # 出错时回滚
        return {
            'status': 'error',
            'message': str(e)
        }, 500
    finally:
        cursor.close()
        db.close()


@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    output_dir = r"C:\Users\yxy\PycharmProjects\pythonProject\app\img"
    return send_from_directory(output_dir, filename, as_attachment=True)

@app.route('/img/<filename>')
def serve_image(filename):
    return send_from_directory('app/img', filename, as_attachment=False)
@app.route('/api/bleu-averages')
def calculate_bleu_averages():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        # 计算中译英方向的平均分
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN type = 0 THEN first_score ELSE NULL END) as zh_en_first,
                AVG(CASE WHEN type = 0 THEN improve_score ELSE NULL END) as zh_en_improve,
                AVG(CASE WHEN type = 1 THEN first_score ELSE NULL END) as en_zh_first,
                AVG(CASE WHEN type = 1 THEN improve_score ELSE NULL END) as en_zh_improve
            FROM bleu_results
        """)
        result = cursor.fetchone()

        return {
            'zh_en': {
                'first': round(float(result['zh_en_first'] or 0), 4),
                'improve': round(float(result['zh_en_improve'] or 0), 4)
            },
            'en_zh': {
                'first': round(float(result['en_zh_first'] or 0), 4),
                'improve': round(float(result['en_zh_improve'] or 0), 4)
            }
        }
    except Exception as e:
        print(f"计算平均分出错: {e}")
        return {
            'zh_en': {'first': 0, 'improve': 0},
            'en_zh': {'first': 0, 'improve': 0}
        }
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
