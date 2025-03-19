from flask import Flask, render_template, request, jsonify
import json
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# データ保存用ディレクトリ
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Google Spreadsheet設定
SPREADSHEET_ID = "1mN1keXe5DvPxIf_BQPXAPvoUCZD1g9jnNQ5fM0v8mKE"  # スプレッドシートのID
WORKSHEET_NAME = "テストラン記録"  # ワークシート名（必要に応じて）
CREDENTIALS_FILE = "sprc25-8b7061e7eca1.json"  # サービスアカウントの認証情報ファイル

# Googleスプレッドシートへの接続を設定
def connect_to_sheets():
    # 正しいスコープを設定
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(credentials)
        
        # スプレッドシートをIDで開く
        try:
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            
            # 既存のワークシートを探す、なければ作成
            try:
                worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=25)
                # ヘッダー行を設定
                worksheet.append_row([
                "日付", "チーム番号", "チーム名", "大学名",
                "黒板消し回収タイム", "ボール回収タイム", "スラロームタイム" ,
                "総時間（ミリ秒）", "黒板消し回収", "黒板消し納品", 
                "ボール回収", "ボール納品", "コートの色", "Vゴール", "備考"
                ])
            
            return worksheet
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"スプレッドシートID: {SPREADSHEET_ID} が見つかりません")
            return None
    except Exception as e:
        print(f"Googleスプレッドシートへの接続エラー: {e}")
        return None

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
    
    # ローカルファイルに保存
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # コンソールにも出力
    print(f"テストラン結果: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # Googleスプレッドシートにも保存
    try:
        worksheet = connect_to_sheets()
        if worksheet:
            # チームの大学名を取得
            university = next((team["university"] for team in TEAM_DATA if team["number"] == data.get("teamNumber")), "不明")
            
            # スプレッドシートに追加する行データを作成
            row_data = [
                data.get("date", ""),  # 日付
                data.get("teamNumber", ""),  # チーム番号
                data.get("teamName", ""),  # チーム名
                university,  # 大学名
                data.get("laps", "")[0]["time"],  # 黒板消し回収タイム
                data.get("laps", "")[1]["time"],  # ボール回収タイム
                data.get("laps", "")[2]["time"],  # スラロームタイム
                data.get("totalTime", ""),  # 総時間
                data.get("eraserCollected", ""),  # 黒板消し回収
                data.get("eraserDelivered", ""),  # 黒板消し納品
                data.get("ballCollected", ""),  # ボール回収
                data.get("ballDelivered", ""),  # ボール納品
                data.get("courtColor", ""),  # コートカラー
                "達成" if data.get("vGoal", False) else "未達成",  # Vゴール
                data.get("notes", ""),  # 備考
            ]
            
            # スプレッドシートに追加
            worksheet.append_row(row_data)
            print("Google Spreadsheetに保存しました")
            print(data)
    except Exception as e:
        print(f"Google Spreadsheetへの保存エラー: {e}")
        import traceback
        traceback.print_exc()  # 詳細なエラー情報を表示
    
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
    app.run(debug=True, port=8000)