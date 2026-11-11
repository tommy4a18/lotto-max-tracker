import json
import os
import requests

def fetch_latest_lotto_max_api():
    # PlayNow 官方彩票數據 API 端點
    url = "https://www.playnow.com/services/lottery/lotto-max/winning-numbers"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.playnow.com/lottery/lotto-max-winning-numbers/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data:
                print("成功從 PlayNow 官方 API 獲取最新開彩數據。")
                return data
    except Exception as e:
        # 僅在背景記錄日誌，絕不製造多餘警報或恐慌
        print(f"提示：無法連線至官方 API 或暫受網絡限制 ({e})，本次將保持現狀。")
        
    # 嚴格拒絕造假：無法取得真實數據時返回 None
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

    # 嘗試從官方獲取最新真實數據
    latest_draw = fetch_latest_lotto_max_api()
    
    # 只有在 100% 取得真實官方數據的情況下才進行寫入
    if latest_draw:
        if not any(item.get('date') == latest_draw.get('date') for item in existing_data):
            existing_data.insert(0, latest_draw)
            print(f"成功新增真實開彩日期: {latest_draw.get('date')}")
            
            # 寫回 JSON 檔案
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            print(f"{filename} 更新成功！")
        else:
            print("該日期的開彩記錄已經存在於歷史數據中，無需重複新增。")
    else:
        # 安靜跳過：保護公共前端頁面，不寫入假數據，亦不強行報錯中斷
        print("提示：本次未能取得最新官方數據，維持現有歷史記錄完整性不變。")

if __name__ == "__main__":
    update_json()
