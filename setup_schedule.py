import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
SCRIPT_PATH = BASE_DIR / "send_reminder.py"
PYTHON_EXE = sys.executable


def create_fixed_task(time_str: str):
    task_name = f"MotivationMailer_Fixed_{time_str.replace(':', '')}"
    tr_command = f'"{PYTHON_EXE}" "{SCRIPT_PATH}" --fixed'
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", tr_command,
        "/sc", "daily", "/st", time_str,
        "/f",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return task_name, result


def create_random_task():
    task_name = "MotivationMailer_Random"
    tr_command = f'"{PYTHON_EXE}" "{SCRIPT_PATH}"'
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", tr_command,
        "/sc", "minute", "/mo", "30",
        "/f",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return task_name, result


def ask_time(prompt: str) -> str:
    while True:
        raw = input(prompt).strip()
        if not raw:
            return ""
        parts = raw.split(":")
        if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
            print("格式不對,要是HH:MM,例如08:00,請重新輸入。")
            continue
        hh, mm = int(parts[0]), int(parts[1])
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            print("時間範圍不對,請重新輸入。")
            continue
        return f"{hh:02d}:{mm:02d}"


def main():
    print("=== 動力提醒信 排程設定精靈 ===\n")

    fixed_times = []
    print("先設定「固定時間」提醒。輸入時間(格式HH:MM,例如08:00),一次一個。")
    print("全部輸入完之後,直接按Enter(不輸入任何東西)結束。\n")
    while True:
        t = ask_time(f"第{len(fixed_times) + 1}個固定時間(直接Enter結束): ")
        if not t:
            break
        fixed_times.append(t)

    print(f"\n你設定了{len(fixed_times)}個固定時間: {fixed_times}\n")

    for t in fixed_times:
        task_name, result = create_fixed_task(t)
        if result.returncode == 0:
            print(f"已建立排程:{task_name}(每天{t})")
        else:
            print(f"建立排程失敗:{task_name}")
            print(result.stderr)

    ans = input(
        "\n要不要也設定「不固定時間」排程"
        "(每30分鐘檢查一次,在時間窗口內用機率決定要不要寄)? (y/n): "
    ).strip().lower()
    if ans == "y":
        task_name, result = create_random_task()
        if result.returncode == 0:
            print(f"已建立排程:{task_name}(每30分鐘檢查一次)")
        else:
            print(f"建立排程失敗:{task_name}")
            print(result.stderr)

    print("\n完成。可以打開Windows「工作排程器」搜尋MotivationMailer開頭的項目確認,")
    print("要刪除某個排程可以在工作排程器裡右鍵刪除,或指令:schtasks /delete /tn 排程名稱 /f")


if __name__ == "__main__":
    main()
