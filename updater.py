import json
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_latest_from_lottonumbers():
    url = "https://ca.lottonumbers.com/lotto-max/past-numbers"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # 進行最多 3 次重試，應付短暫嘅網絡波動或伺服器忙碌
    for attempt in range(3):
        try:
            print(f"嘗試連線至 ca.lottonumbers.com (第 {attempt + 1} 次)...")
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.select('tr, .past-result-row, table tr')
                
                for row in rows:
                    date_el = row.select_one('td:first-child, .date-cell')
                    balls_container = row.select_one('ul.balls')
                    
                    if date_el and balls_container:
                        date_text = date_el.get_text(strip=True)
                        ball_elements = balls_container.select('li.ball')
                        numbers = []
                        bonus = 0
                        
                        for i, b in enumerate(ball_elements):
                            try:
                                val = int(b.get_text(strip=True))
                                if i < 7:
                                    numbers.append(val)
                                else:
                                    bonus = val
                            except ValueError:
                                continue
                                
                        if len(numbers) >= 7:
                            try:
                                clean_date_str = " ".join([w for w in date_text.split() if w not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']])
                                parsed_date = datetime.strptime(clean_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                            except Exception:
                                parsed_date = datetime.now().strftime("%Y-%m-%d")
                                
                            latest_draw = {
                                "date": parsed_date,
                                "numbers": sorted(numbers[:7]),
                                "bonus": bonus if bonus != 0 else (int(ball_elements[7].get_text(strip=True)) if len(ball_elements) > 7 else 0)
                            }
                            
                            print(f"成功抓取最新真實開彩數據：{parsed_date}")
                            return latest_draw
                            
        except Exception as e:
            print(f"第 {attempt + 1} 次連線失敗: {e}")
            time.sleep(3) # 等待 3 秒後重試
            
    return None

def update_json():
    filename = "lotto_max_history.json"
    
    existing_data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []

    latest_draw = fetch_latest_from_lottonumbers()
    
    if latest_draw:
        if not any(item.get('date') == latest_draw.get('date') for item in existing_data):
            existing_data.insert(0, latest_draw)
            print(f"成功新增真實開彩日期: {latest_draw.get('date')}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 更新成功！")
        else:
            print("該日期的開彩記錄已經存在於歷史數據中。")
    else:
        print("提示：本次未能取得最新數據，維持現有歷史記錄完整性不變。")

if __name__ == "__main__":
    update_json()
