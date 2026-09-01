import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PREFIX = "MotivationMailer"


def list_tasks():
    result = subprocess.run(
        ["schtasks", "/query", "/fo", "csv", "/nh"],
        capture_output=True, text=True,
    )
    task_names = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        first_field = line.split(",")[0].strip('"')
        if PREFIX in first_field:
            task_names.append(first_field)
    return task_names


def main():
    tasks = list_tasks()
    if not tasks:
        print("沒有找到任何 MotivationMailer 開頭的排程,可能已經刪除過了。")
        return

    print(f"找到{len(tasks)}個排程,準備全部刪除:")
    for t in tasks:
        print(f" - {t}")
    print()

    for t in tasks:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", t, "/f"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"已刪除:{t}")
        else:
            print(f"刪除失敗:{t}")
            print(result.stderr)

    print("\n全部排程已清除,不會再寄信。之後想重新開始,雙擊 02.設定排程.bat 重新設定即可。")


if __name__ == "__main__":
    main()
