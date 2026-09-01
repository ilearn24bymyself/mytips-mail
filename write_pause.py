from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PAUSE_FLAG_PATH = BASE_DIR / "pause.flag"

today_str = datetime.now().strftime("%Y%m%d")
PAUSE_FLAG_PATH.write_text(today_str, encoding="utf-8")
print(f"已暫停今天({today_str})的提醒信件,明天會自動恢復。")
