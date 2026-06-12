"""任务数据持久化模块，负责 JSON 文件的读写。"""

import json
import logging
import os

logger = logging.getLogger("campus_task")

TASKS_FILE = "tasks.json"


def load_tasks():
    """从 JSON 文件加载任务列表。文件不存在、为空或损坏时返回空列表。"""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            logger.warning("tasks.json 存在但为空，视为空列表。")
            return []
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error("tasks.json 格式损坏，已重置为空列表。")
        return []


def save_tasks(tasks):
    """将任务列表写入 JSON 文件。"""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    logger.info(f"已保存 {len(tasks)} 条任务到 {TASKS_FILE}")
