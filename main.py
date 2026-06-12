import json
import os
import sys
from datetime import datetime

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def add_task(title):
    tasks = load_tasks()
    task = {
        "id": get_next_id(tasks),
        "title": title,
        "status": "todo",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"已添加任务 [{task['id']}]: {task['title']}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("暂无任务。")
        return
    for task in tasks:
        status = "[x]" if task["status"] == "done" else "[ ]"
        print(f"  [{status}] {task['id']}. {task['title']} ({task['created_at']})")


def done_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == "done":
                print(f"任务 [{task_id}] 已经是完成状态。")
                return
            task["status"] = "done"
            save_tasks(tasks)
            print(f"任务 [{task_id}] 已标记为完成: {task['title']}")
            return
    print(f"任务 [{task_id}] 不存在。")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python main.py add <任务标题>")
        print("  python main.py list")
        print("  python main.py done <任务编号>")
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("请提供任务标题。用法: python main.py add <任务标题>")
            return
        title = sys.argv[2]
        add_task(title)
    elif command == "list":
        list_tasks()
    elif command == "done":
        if len(sys.argv) < 3:
            print("请提供任务编号。用法: python main.py done <任务编号>")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("任务编号必须是整数。")
            return
        done_task(task_id)
    else:
        print(f"未知命令: {command}")
        print("可用命令: add, list, done")


if __name__ == "__main__":
    main()
