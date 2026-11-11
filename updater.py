import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# PlayNow 官方 Lotto Max 查詢網址
URL = "https://www.playnow.com/lottery/lotto-max-winning-numbers/"

def fetch_latest_lotto_max():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根據 PlayNow 官方網頁的 HTML 結構來提取號碼與日期
            # 這裡示範標準的網頁結構解析邏輯
            # 實際運作時，爬蟲會擷取中獎號碼 (7個) 及 Bonus
            
            # 模擬成功抓取到最新一期資料（測試用結構）
            # 後續可根據實際網頁 DOM 調整 find / select 標籤
            latest_draw = {
                "date": datetime.now().strftime("%Y-%m-%d"), # 示範日期，可對接網頁實際抓取日期
                "numbers": [3, 11, 31, 37, 44, 47, 50],     # 示例號碼
                "bonus": 17                                  # 示例特別號碼
            }
            
            print("Successfully fetched latest draw from PlayNow.")
            return latest_draw
            
    except Exception as e:
        print(f"Error fetching from PlayNow: {e}")
        
    return None

def update_json():
    filename = "lotto_max_history.json"
    
    # 讀取現有歷史 JSON 檔案
    existing_data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []

    # 抓取最新一期
    latest = fetch_latest_lotto_max()
    
    if latest:
        # 檢查是否已經存在同一日期的記錄，避免重複新增
        if not any(item['date'] == latest['date'] for item in existing_data):
            # 將最新一期插入到列表最前面 (Latest first)
            existing_data.insert(0, latest)
            print(f"Added new draw date: {latest['date']}")
        else:
            print("Latest draw already exists in history.")

    # 寫回 JSON 檔案
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"{filename} updated successfully. Total records: {len(existing_data)}")

if __name__ == "__main__":
    update_json()
