from flask import Flask, render_template, request, jsonify
import json
import datetime
import os

app = Flask(__name__)

# データ保存用ディレクトリ
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# チームデータ
TEAM_DATA = [
    { "number": "T01", "name": "蜜熊工房", "university": "群馬工業高等専門学校" },
    { "number": "T02", "name": "はちのこ☆ロボコンズ", "university": "豊橋技術科学大学" },
    { "number": "T03", "name": "ハニーワーカー", "university": "東京大学" },
    { "number": "T04", "name": "回熊", "university": "横浜国立大学" },
    { "number": "T05", "name": "精蜜研", "university": "千葉工業大学" },
    { "number": "T06", "name": "しゅんぶんぶん", "university": "東京大学" },
    { "number": "T07", "name": "大熊猫", "university": "福島工業高等専門学校" },
    { "number": "T08", "name": "とある蜂蜜の射出機構", "university": "電気通信大学" },
    { "number": "T09", "name": "大熊重信", "university": "早稲田大学" },
    { "number": "T10", "name": "蜂蜂金蜜", "university": "金沢工業大学" },
    { "number": "T11", "name": "ずっと最速で良いのに", "university": "早稲田大学" },
    { "number": "T12", "name": "Maquinista", "university": "東京科学大学" },
    { "number": "T13", "name": "科学技術研究部", "university": "新潟大学" },
    { "number": "T14", "name": "B", "university": "千葉大学" },
    { "number": "T15", "name": "情メカ", "university": "群馬大学" },
    { "number": "T16", "name": "蜜のメカ探検隊", "university": "慶應義塾大学" },
    { "number": "T17", "name": "ハニーギャザーズ", "university": "都立産業技術高等専門学校" },
    { "number": "T18", "name": "はにかむメカ", "university": "東京工科大学" },
    { "number": "T19", "name": "鵥", "university": "東京工業高等専門学校" },
    { "number": "T20", "name": "ヴォイテック隊長", "university": "東京工業高等専門学校" },
    { "number": "T21", "name": "BeeMead", "university": "東京工業高等専門学校" }
];


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams', methods=['GET'])
def get_teams():
    return jsonify(TEAM_DATA)

@app.route('/save_record', methods=['POST'])
def save_record():
    data = request.json
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    # ファイル名にチーム情報を含める
    team_info = f"{data.get('teamNumber', 'unknown')}_{data.get('teamName', 'unknown')}"
    filename = f"{DATA_DIR}/record_{team_info}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # コンソールにも出力
    print(f"テストラン結果: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    return jsonify({"status": "success", "filename": filename})

@app.route('/get_records', methods=['GET'])
def get_records():
    records = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith('record_') and filename.endswith('.json'):
            with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
                record = json.load(f)
                record['filename'] = filename
                records.append(record)
    
    # 日付順に並べ替え
    records.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True)