import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_from_playnow():
    # PlayNow 官方 Lotto Max 查詢網址
    url = "https://www.playnow.com/lottery/lotto-max-winning-numbers/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            numbers = []
            # 尋找頁面中的號碼元素
            number_elements = soup.select('.winning-number, .ball, .lotto-number')
            for el in number_elements:
                try:
                    num = int(el.text.strip())
                    if num not in numbers:
                        numbers.append(num)
                except ValueError:
                    continue
            
            # 如果成功抓取到足夠號碼
            if len(numbers) >= 7:
                latest_draw = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "numbers": sorted(numbers[:7]),
                    "bonus": numbers[7] if len(numbers) > 7 else 0
                }
                print("成功從 PlayNow 官網抓取真實數據！")
                return latest_draw
                
    except Exception as e:
        print(f"連線或解析 PlayNow 官網時發生錯誤: {e}")
        
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

    # 嘗試從官網抓取最新數據
    latest_draw = fetch_from_playnow()
    
    if latest_draw:
        if not any(item['date'] == latest_draw['date'] for item in existing_data):
            existing_data.insert(0, latest_draw)
            print(f"成功新增官網最新日期: {latest_draw['date']}")
        else:
            print("該日期的開彩記錄已存在於 JSON 中。")
    else:
        print("未能成功取得官網數據（可能受防爬蟲限制）。")

    # 寫回 JSON 檔案
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
    print(f"{filename} 更新完成！目前總記錄數: {len(existing_data)}")

if __name__ == "__main__":
    update_json()
