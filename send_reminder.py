import argparse
import json
import random
import smtplib
import ssl
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.local.json"
MESSAGES_PATH = BASE_DIR / "messages.txt"
PAUSE_FLAG_PATH = BASE_DIR / "pause.flag"

WEEKDAY_WINDOW = (17, 22)  # 平日:17:00~22:00
WEEKEND_WINDOW = (6, 22)   # 假日:06:00~22:00

# 排程器每CHECK_INTERVAL_MINUTES分鐘檢查一次(要跟02.設定排程.bat建立的排程間隔一致)
CHECK_INTERVAL_MINUTES = 30
TARGET_RANDOM_EMAILS_PER_DAY = 4  # 平日/假日都抓這個平均封數

def _checks_in_window(window: tuple) -> float:
    hours = window[1] - window[0]
    return hours * 60 / CHECK_INTERVAL_MINUTES

WEEKDAY_SEND_PROBABILITY = TARGET_RANDOM_EMAILS_PER_DAY / _checks_in_window(WEEKDAY_WINDOW)
WEEKEND_SEND_PROBABILITY = TARGET_RANDOM_EMAILS_PER_DAY / _checks_in_window(WEEKEND_WINDOW)


def is_paused_today(now: datetime) -> bool:
    if not PAUSE_FLAG_PATH.exists():
        return False
    flag_content = PAUSE_FLAG_PATH.read_text(encoding="utf-8").strip()
    today_str = now.strftime("%Y%m%d")
    return flag_content == today_str


def in_time_window(now: datetime) -> bool:
    is_weekend = now.weekday() >= 5  # 5=Sat, 6=Sun
    start, end = WEEKEND_WINDOW if is_weekend else WEEKDAY_WINDOW
    return start <= now.hour < end


def current_probability(now: datetime) -> float:
    is_weekend = now.weekday() >= 5  # 5=Sat, 6=Sun
    return WEEKEND_SEND_PROBABILITY if is_weekend else WEEKDAY_SEND_PROBABILITY


def load_random_message() -> str:
    lines = [
        line.strip()
        for line in MESSAGES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not lines:
        raise RuntimeError("messages.txt 沒有任何訊息可以寄")
    return random.choice(lines)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def send_email(subject: str, body: str) -> None:
    config = load_config()
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = config["gmail_address"]
    msg["To"] = config["recipient"]

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(config["gmail_address"], config["gmail_app_password"])
        server.send_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run", action="store_true", help="只印出判斷結果,不實際寄信"
    )
    parser.add_argument(
        "--force", action="store_true", help="略過時間窗口與機率判斷,直接寄一封(測試用)"
    )
    parser.add_argument(
        "--fixed",
        action="store_true",
        help="固定時間排程專用:略過時間窗口與機率判斷,但仍檢查暫停旗標",
    )
    args = parser.parse_args()

    now = datetime.now()

    if is_paused_today(now):
        print(f"[{now}] 今天已設定暫停,不寄信。")
        return

    if not args.force and not args.fixed:
        if not in_time_window(now):
            print(f"[{now}] 不在允許的時間窗口內,不寄信。")
            return
        if random.random() >= current_probability(now):
            print(f"[{now}] 在時間窗口內,但這次機率沒中,不寄信。")
            return

    message = load_random_message()
    subject = "給自己的提醒"

    if args.dry_run:
        print(f"[{now}] dry-run:會寄出的內容如下,但不會實際寄送。")
        print(f"主旨:{subject}")
        print(f"內文:{message}")
        return

    send_email(subject, message)
    print(f"[{now}] 已寄出:{message}")


if __name__ == "__main__":
    main()
