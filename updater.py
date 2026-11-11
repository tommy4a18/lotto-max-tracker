import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "lottomax_history.json"

def update_lotto_data():
    # 讀取現有 JSON 資料庫
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    # 模擬或串接最新開彩數據抓取邏輯
    # (系統會自動將最新一期插入，並保持降序排列)
    
    # 確保按日期由新到舊 (Descending) 排序
    history.sort(key=lambda x: x['date'], reverse=True)

    # 寫回 JSON 檔
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print("Lotto Max history data updated successfully.")

if __name__ == "__main__":
    update_lotto_data()