"""任务数据持久化模块，负责 JSON 文件的读写。"""

import json
import os

TASKS_FILE = "tasks.json"


def load_tasks():
    """从 JSON 文件加载任务列表。文件不存在时返回空列表。"""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_tasks(tasks):
    """将任务列表写入 JSON 文件。"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
