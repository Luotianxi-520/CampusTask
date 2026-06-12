"""任务管理模块，提供任务的增删改查等业务逻辑。"""

from datetime import datetime
from storage import load_tasks, save_tasks


def get_next_id(tasks):
    """基于历史最大 ID 生成新任务编号，确保编号唯一且递增。"""
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1


def add_task(title, priority=None):
    """添加新任务，返回创建的任务对象。标题为空时抛出 ValueError。
    priority 为可选的优先级: high / medium / low。
    """
    if not title or not title.strip():
        raise ValueError("任务标题不能为空")
    tasks = load_tasks()
    task = {
        "id": get_next_id(tasks),
        "title": title,
        "status": "todo",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if priority:
        task["priority"] = priority
    tasks.append(task)
    save_tasks(tasks)
    return task


def list_tasks():
    """返回所有任务列表。"""
    return load_tasks()


def done_task(task_id):
    """将指定编号的任务标记为完成。
    返回 (success, message) 元组。
    """
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            if task["status"] == "done":
                return False, f"任务 [{task_id}] 已经是完成状态。"
            task["status"] = "done"
            save_tasks(tasks)
            return True, f"任务 [{task_id}] 已标记为完成: {task['title']}"
    return False, f"任务 [{task_id}] 不存在。"


def delete_task(task_id):
    """删除指定编号的任务。
    返回 (success, message) 元组。
    """
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            removed = tasks.pop(i)
            save_tasks(tasks)
            return True, f"任务 [{task_id}] 已删除: {removed['title']}"
    return False, f"任务 [{task_id}] 不存在。"


def search_tasks(keyword):
    """模糊搜索标题中包含 keyword 的任务，返回匹配的任务列表。"""
    tasks = load_tasks()
    keyword_lower = keyword.lower()
    return [t for t in tasks if keyword_lower in t["title"].lower()]


def get_stats():
    """返回任务统计信息，包含 total、done、todo 数量。"""
    tasks = load_tasks()
    done_count = sum(1 for t in tasks if t["status"] == "done")
    return {
        "total": len(tasks),
        "done": done_count,
        "todo": len(tasks) - done_count,
    }
