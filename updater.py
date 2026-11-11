import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_latest_from_lottonumbers():
    url = "https://ca.lottonumbers.com/lotto-max/past-numbers"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根據截圖中的結構，每一行歷史記錄通常在表格的 tr 裡面
            # 我們尋找包含 .balls 的行
            rows = soup.select('tr, .past-result-row, table tr')
            
            for row in rows:
                # 尋找日期
                date_el = row.select_one('td:first-child, .date-cell')
                balls_container = row.select_one('ul.balls')
                
                if date_el and balls_container:
                    date_text = date_el.get_text(strip=True)
                    
                    # 提取所有球的數字
                    ball_elements = balls_container.select('li.ball')
                    numbers = []
                    bonus = 0
                    
                    for i, b in enumerate(ball_elements):
                        try:
                            val = int(b.get_text(strip=True))
                            if i < 7:
                                numbers.append(val)
                            else:
                                bonus = val # 第 8 個或帶有 bonus class 的通常是 Bonus/BB
                        except ValueError:
                            continue
                            
                    # 如果成功抓到 7 個主號碼
                    if len(numbers) >= 7:
                        # 嘗試將英文日期轉為標準 YYYY-MM-DD 格式
                        try:
                            # 假設格式如 "Tuesday November 10 2026" 或 "November 10 2026"
                            clean_date_str = " ".join([w for w in date_text.split() if not w in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']])
                            parsed_date = datetime.strptime(clean_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                        except Exception:
                            parsed_date = datetime.now().strftime("%Y-%m-%d")
                            
                        latest_draw = {
                            "date": parsed_date,
                            "numbers": sorted(numbers[:7]),
                            "bonus": bonus if bonus != 0 else (int(ball_elements[7].get_text(strip=True)) if len(ball_elements) > 7 else 0)
                        }
                        
                        print(f"成功從 ca.lottonumbers.com 抓取最新真實開彩數據：{parsed_date}")
                        return latest_draw
                        
    except Exception as e:
        print(f"提示：爬取 ca.lottonumbers.com 時發生連線或解析錯誤 ({e})，本次保持現狀。")
        
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

    # 嘗試抓取最新真實數據
    latest_draw = fetch_latest_from_lottonumbers()
    
    if latest_draw:
        # 檢查是否已存在該日期，避免重複
        if not any(item.get('date') == latest_draw.get('date') for item in existing_data):
            existing_data.insert(0, latest_draw)
            print(f"成功新增真實開彩日期: {latest_draw.get('date')}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 更新成功！")
        else:
            print("該日期的開彩記錄已經存在於歷史數據中，無需重複新增。")
    else:
        print("提示：本次未能取得最新數據，維持現有歷史記錄完整性不變（零假數據、零報錯）。")

if __name__ == "__main__":
    update_json()
