import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_latest_lotto_max_wclc():
    # 使用 WCLC 官方 Lotto Max 頁面
    url = "https://www.wclc.com/games/lotto-max.htm"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 從 WCLC 頁面結構中提取中獎號碼
            # 通常官方會用特定的 class 標示開彩號碼
            numbers = []
            number_elements = soup.select('.winning-number, .ball, .number, span.game-ball')
            for el in number_elements:
                try:
                    num = int(el.text.strip())
                    if num not in numbers:
                        numbers.append(num)
                except ValueError:
                    continue
            
            # 如果成功抓取到足夠的號碼（7個主號碼 + 1個Bonus）
            if len(numbers) >= 7:
                latest_draw = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "numbers": sorted(numbers[:7]),
                    "bonus": numbers[7] if len(numbers) > 7 else 0
                }
                print("成功從 WCLC 官網獲取最新開彩數據。")
                return latest_draw
                
    except Exception as e:
        print(f"提示：無法連線至 WCLC 官方網頁 ({e})，本次將保持現狀。")
        
    # 絕不造假：抓取失敗時返回 None，安全安靜跳過
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

    # 嘗試從 WCLC 獲取最新真實數據
    latest_draw = fetch_latest_lotto_max_wclc()
    
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
        print("提示：本次未能取得 WCLC 最新官方數據，維持現有歷史記錄完整性不變。")

if __name__ == "__main__":
    update_json()
