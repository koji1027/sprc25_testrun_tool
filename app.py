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
    {"number": "T01", "name": "ロボ太郎", "university": "東京工科大学"},
    {"number": "T02", "name": "メカニカ", "university": "大阪工業大学"},
    {"number": "T03", "name": "テクノブレイン", "university": "京都大学"},
    {"number": "T04", "name": "ロボマスターズ", "university": "名古屋大学"},
    {"number": "T05", "name": "AI機械", "university": "東北大学"}
]

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