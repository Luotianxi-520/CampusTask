"""命令行接口模块，负责参数解析、命令分发和结果输出。"""

import sys
import task_manager as tm


def print_usage():
    """输出使用说明。"""
    print("用法:")
    print("  python main.py add <任务标题>")
    print("  python main.py list [--status done|todo] [--sort deadline]")
    print("  python main.py done <任务编号>")
    print("  python main.py delete <任务编号>")
    print("  python main.py search <关键词>")
    print("  python main.py edit <任务编号> <新标题>")
    print("  python main.py export <文件路径>")
    print("  python main.py stats")


def handle_add(args):
    if len(args) < 1:
        print("请提供任务标题。用法: python main.py add <任务标题> [--deadline YYYY-MM-DD] [--priority high|medium|low]")
        return
    title = args[0]
    deadline = None
    priority = None
    for i, arg in enumerate(args):
        if arg == "--deadline" and i + 1 < len(args):
            deadline = args[i + 1]
        elif arg == "--priority" and i + 1 < len(args):
            priority = args[i + 1]
    try:
        task = tm.add_task(title, deadline=deadline, priority=priority)
    except ValueError as e:
        print(str(e))
        return
    msg = f"已添加任务 [{task['id']}]: {task['title']}"
    if deadline:
        msg += f" (截止: {deadline})"
    if priority:
        msg += f" (优先级: {priority})"
    print(msg)


def handle_list(args=None):
    status_filter = None
    sort_by = None
    if args:
        for i, arg in enumerate(args):
            if arg == "--status" and i + 1 < len(args):
                status_filter = args[i + 1]
            elif arg == "--sort" and i + 1 < len(args):
                sort_by = args[i + 1]
    tasks = tm.list_tasks(status_filter=status_filter, sort_by=sort_by)
    if not tasks:
        label = status_filter if status_filter else "任何"
        print(f"暂无{label}任务。")
        return
    for task in tasks:
        status = "[x]" if task["status"] == "done" else "[ ]"
        line = f"  [{status}] {task['id']}. {task['title']} ({task['created_at']})"
        if task.get("deadline"):
            line += f"  截止: {task['deadline']}"
        if task.get("priority"):
            line += f"  [{task['priority']}]"
        print(line)


def handle_done(args):
    if len(args) < 1:
        print("请提供任务编号。用法: python main.py done <任务编号>")
        return
    try:
        task_id = int(args[0])
    except ValueError:
        print("任务编号必须是整数。")
        return
    success, message = tm.done_task(task_id)
    print(message)


def handle_delete(args):
    if len(args) < 1:
        print("请提供任务编号。用法: python main.py delete <任务编号>")
        return
    try:
        task_id = int(args[0])
    except ValueError:
        print("任务编号必须是整数。")
        return
    success, message = tm.delete_task(task_id)
    print(message)


def handle_edit(args):
    if len(args) < 2:
        print("请提供任务编号和新标题。用法: python main.py edit <任务编号> <新标题>")
        return
    try:
        task_id = int(args[0])
    except ValueError:
        print("任务编号必须是整数。")
        return
    new_title = args[1]
    try:
        success, message = tm.edit_task(task_id, new_title)
    except ValueError as e:
        print(str(e))
        return
    print(message)


def handle_export(args):
    if len(args) < 1:
        print("请提供文件路径。用法: python main.py export <文件路径>")
        return
    filepath = args[0]
    count = tm.export_csv(filepath)
    print(f"已导出 {count} 条任务到 {filepath}")


def handle_search(args):
    if len(args) < 1:
        print("请提供搜索关键词。用法: python main.py search <关键词>")
        return
    keyword = args[0]
    results = tm.search_tasks(keyword)
    if not results:
        print(f"未找到包含 '{keyword}' 的任务。")
        return
    print(f"搜索 '{keyword}' 的结果 ({len(results)} 条):")
    for task in results:
        status = "[x]" if task["status"] == "done" else "[ ]"
        print(f"  [{status}] {task['id']}. {task['title']} ({task['created_at']})")


def handle_stats():
    stats = tm.get_stats()
    print(f"总任务数: {stats['total']}")
    print(f"已完成:   {stats['done']}")
    print(f"待办:     {stats['todo']}")


COMMANDS = {
    "add": handle_add,
    "list": handle_list,
    "done": handle_done,
    "delete": handle_delete,
    "edit": handle_edit,
    "export": handle_export,
    "search": handle_search,
    "stats": handle_stats,
}


def dispatch(command, args):
    """根据命令名分发到对应处理函数。"""
    if command in COMMANDS:
        handler = COMMANDS[command]
        if command == "stats":
            handler()
        elif command == "list":
            handler(args)
        else:
            handler(args)
    else:
        print(f"未知命令: {command}")
        print("可用命令: add, list, done, delete, edit, export, search, stats")


def main(argv=None):
    """命令行入口：解析参数并分发命令。"""
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print_usage()
        return

    command = argv[1]
    args = argv[2:]
    dispatch(command, args)
