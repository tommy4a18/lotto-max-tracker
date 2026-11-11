import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_latest_from_lotto8():
    url = "https://www.lotto-8.com/canada/listltoCAMAX.asp"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # 確保正確解碼（通常這類網站用 utf-8 或 big5/cp950，視乎實際編碼，多數 utf-8 搞掂）
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 這裡示範從 lotto-8 的 HTML 表格或列表尋找開彩數據
            # 通常最新一期會排在最前面
            numbers = []
            
            # 尋找頁面中符合開彩波號的元素（可根據實際頁面 class 調整）
            number_elements = soup.select('.td_numb, .ball, font[color], td span')
            for el in number_elements:
                text = el.text.strip()
                if text.isdigit():
                    num = int(text)
                    if 1 <= num <= 50 and num not in numbers:
                        numbers.append(num)
            
            # Lotto Max 每期主號碼 7 個 + 1個 Bonus (共 8 個或以上)
            if len(numbers) >= 7:
                latest_draw = {
                    "date": datetime.now().strftime("%Y-%m-%d"), # 後續可精準從表格抓取對應日期
                    "numbers": sorted(numbers[:7]),
                    "bonus": numbers[7] if len(numbers) > 7 else 0
                }
                print("成功從 lotto-8.com 抓取最新真實開彩數據！")
                return latest_draw
                
    except Exception as e:
        print(f"提示：連線至 lotto-8.com 時發生錯誤 ({e})，本次保持現狀。")
        
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
    latest_draw = fetch_latest_from_lotto8()
    
    if latest_draw:
        if not any(item.get('date') == latest_draw.get('date') for item in existing_data):
            existing_data.insert(0, latest_draw)
            print(f"成功新增真實開彩日期: {latest_draw.get('date')}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 更新成功！")
        else:
            print("該日期的記錄已經存在於歷史數據中。")
    else:
        print("提示：本次未能取得最新數據，維持現有歷史記錄完整性不變。")

if __name__ == "__main__":
    update_json()
