"""命令行接口模块，基于 argparse 提供参数解析和命令分发。"""

import argparse
from . import task_manager as tm
from . import __version__


def build_parser():
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        prog="campus-task",
        description="校园任务清单 — 命令行任务管理工具",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"campus-task {__version__}",
    )

    sub = parser.add_subparsers(dest="command", title="可用命令")

    # add
    p = sub.add_parser("add", help="添加新任务")
    p.add_argument("title", help="任务标题")
    p.add_argument("--deadline", help="截止日期 (YYYY-MM-DD)")
    p.add_argument("--priority", choices=["high", "medium", "low"], help="优先级")

    # list
    p = sub.add_parser("list", help="查看任务列表")
    p.add_argument("--status", choices=["todo", "done"], help="按状态过滤")
    p.add_argument("--sort", choices=["deadline"], help="排序方式")

    # done
    p = sub.add_parser("done", help="标记任务为完成")
    p.add_argument("task_id", type=int, help="任务编号")

    # delete
    p = sub.add_parser("delete", help="删除任务")
    p.add_argument("task_id", type=int, help="任务编号")

    # edit
    p = sub.add_parser("edit", help="修改任务标题")
    p.add_argument("task_id", type=int, help="任务编号")
    p.add_argument("new_title", help="新标题")

    # export
    p = sub.add_parser("export", help="导出任务为 CSV")
    p.add_argument("filepath", help="导出文件路径")

    # search
    p = sub.add_parser("search", help="搜索任务")
    p.add_argument("keyword", help="搜索关键词")

    # stats
    sub.add_parser("stats", help="查看统计信息")

    return parser


def dispatch(args):
    """根据解析后的参数分发到对应的业务函数。"""
    cmd = args.command

    if cmd == "add":
        try:
            task = tm.add_task(
                args.title,
                deadline=args.deadline,
                priority=args.priority,
            )
        except ValueError as e:
            print(f"错误: {e}")
            return 1
        msg = f"已添加任务 [{task['id']}]: {task['title']}"
        if args.deadline:
            msg += f" (截止: {args.deadline})"
        if args.priority:
            msg += f" (优先级: {args.priority})"
        print(msg)

    elif cmd == "list":
        tasks = tm.list_tasks(
            status_filter=args.status,
            sort_by=args.sort,
        )
        if not tasks:
            label = args.status if args.status else "任何"
            print(f"暂无{label}任务。")
            return 0
        for task in tasks:
            mark = "[x]" if task["status"] == "done" else "[ ]"
            line = f"  [{mark}] {task['id']}. {task['title']} ({task['created_at']})"
            if task.get("deadline"):
                line += f"  截止: {task['deadline']}"
            if task.get("priority"):
                line += f"  [{task['priority']}]"
            print(line)

    elif cmd == "done":
        success, message = tm.done_task(args.task_id)
        print(message)
        return 0 if success else 1

    elif cmd == "delete":
        success, message = tm.delete_task(args.task_id)
        print(message)
        return 0 if success else 1

    elif cmd == "edit":
        try:
            success, message = tm.edit_task(args.task_id, args.new_title)
        except ValueError as e:
            print(f"错误: {e}")
            return 1
        print(message)
        return 0 if success else 1

    elif cmd == "export":
        count = tm.export_csv(args.filepath)
        print(f"已导出 {count} 条任务到 {args.filepath}")

    elif cmd == "search":
        results = tm.search_tasks(args.keyword)
        if not results:
            print(f"未找到包含 '{args.keyword}' 的任务。")
            return 0
        print(f"搜索 '{args.keyword}' 的结果 ({len(results)} 条):")
        for task in results:
            mark = "[x]" if task["status"] == "done" else "[ ]"
            print(f"  [{mark}] {task['id']}. {task['title']} ({task['created_at']})")

    elif cmd == "stats":
        stats = tm.get_stats()
        print(f"总任务数: {stats['total']}")
        print(f"已完成:   {stats['done']}")
        print(f"待办:     {stats['todo']}")

    return 0


def main(argv=None):
    """命令行入口。"""
    parser = build_parser()

    if argv is not None:
        args = parser.parse_args(argv[1:])
    else:
        args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        return dispatch(args)
    except Exception as e:
        print(f"错误: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
