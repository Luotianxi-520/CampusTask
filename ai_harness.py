"""AI Harness — 自然语言控制 CampusTask 的 AI 代理层。"""

import json
import re
import time
from datetime import datetime

# ── 可用的工具定义 ─────────────────────────────────────────

AVAILABLE_ACTIONS = {
    "add_task": {
        "description": "添加新任务",
        "params": {"title": "str (必填)", "deadline": "str? (YYYY-MM-DD)", "priority": "str? (high/medium/low)"},
    },
    "list_tasks": {
        "description": "查看任务列表",
        "params": {"status_filter": "str? (todo/done)", "sort_by": "str? (deadline/priority)", "overdue_only": "bool?"},
    },
    "done_task": {
        "description": "标记任务为完成",
        "params": {"task_id": "int"},
    },
    "delete_task": {
        "description": "删除指定任务",
        "params": {"task_id": "int"},
    },
    "search_tasks": {
        "description": "搜索任务",
        "params": {"keyword": "str"},
    },
    "get_stats": {
        "description": "获取任务统计信息",
        "params": {},
    },
    "export_csv": {
        "description": "导出任务为 CSV 文件",
        "params": {"filepath": "str"},
    },
}


# ── prompt_builder ────────────────────────────────────────

def prompt_builder(user_input, tasks_state):
    """根据用户输入和当前任务状态构建系统提示词。"""
    state_summary = f"当前有 {len(tasks_state)} 个任务。"
    for t in tasks_state:
        deadline_info = f", 截止: {t['deadline']}" if t.get("deadline") else ""
        priority_info = f", 优先级: {t['priority']}" if t.get("priority") else ""
        state_summary += f"\n  [{t['id']}] {t['title']} ({t['status']}{deadline_info}{priority_info})"

    actions_desc = ""
    for name, info in AVAILABLE_ACTIONS.items():
        actions_desc += f"- {name}: {info['description']}  参数: {info['params']}\n"

    prompt = (
        "你是一个任务管理助手。请将用户的自然语言请求转换为 JSON 格式的操作指令。\n\n"
        f"## 当前状态\n{state_summary}\n\n"
        f"## 可用操作\n{actions_desc}\n"
        '## 输出格式\n{"action": "<action_name>", "args": {...}}\n'
        "只输出 JSON，不要有任何其他文本。\n\n"
        f"## 用户请求\n{user_input}"
    )
    return prompt


# ── mock_model ─────────────────────────────────────────────

def mock_model(prompt):
    """模拟 AI 模型：基于规则匹配将自然语言转换为 JSON 操作。

    生产环境中可替换为真实 LLM API 调用。
    """
    # 提取用户输入（最后一行）
    lines = prompt.strip().split("\n")
    user_input = lines[-1] if lines else ""

    # 尝试提取任务编号
    id_match = re.search(r"第?\s*(\d+)\s*(个|号)?", user_input)

    # 匹配操作类型
    if any(w in user_input for w in ["删除所有", "全部删除", "清空所有"]):
        return '{"action": "delete_all_tasks", "args": {}}'

    if any(w in user_input for w in ["删除", "移除", "去掉"]) and id_match:
        return json.dumps({"action": "delete_task", "args": {"task_id": int(id_match.group(1))}}, ensure_ascii=False)

    if any(w in user_input for w in ["完成", "做完", "标记", "搞定"]) and id_match:
        return json.dumps({"action": "done_task", "args": {"task_id": int(id_match.group(1))}}, ensure_ascii=False)

    if any(w in user_input for w in ["添加", "新建", "增加", "创建一个", "加一个", "加个", "帮我添加"]):
        title = user_input
        for prefix in ["添加", "新建", "增加", "创建一个", "加一个", "加个", "帮我添加", "请", "帮我"]:
            title = title.replace(prefix, "", 1)
        title = title.strip().strip("，。！,.!\"\"''")
        deadline = None
        priority = None
        deadline_match = re.search(r"(截止|deadline|到期)[:：]?\s*(\d{4}-\d{2}-\d{2}|明天|后天|今天)", user_input)
        if deadline_match:
            raw = deadline_match.group(2)
            if raw == "明天":
                deadline = "2026-06-13"
            elif raw == "后天":
                deadline = "2026-06-14"
            elif raw == "今天":
                deadline = "2026-06-12"
            else:
                deadline = raw
        if "高" in user_input or "high" in user_input.lower():
            priority = "high"
        elif "中" in user_input and "优先" in user_input:
            priority = "medium"
        elif "低" in user_input and "优先" in user_input:
            priority = "low"
        return json.dumps({"action": "add_task", "args": {"title": title, "deadline": deadline, "priority": priority}}, ensure_ascii=False)

    if any(w in user_input for w in ["查看", "列出", "显示", "列表", "有哪些", "看看"]):
        sort_by = None
        overdue_only = False
        if any(w in user_input for w in ["优先级", "重要程度"]):
            sort_by = "priority"
        elif any(w in user_input for w in ["截止", "日期", "时间", "deadline"]) and any(w in user_input for w in ["排序", "先后", "顺序"]):
            sort_by = "deadline"
        if any(w in user_input for w in ["逾期", "过期", "过了截止", "超期", "错过"]):
            overdue_only = True
        if sort_by or overdue_only:
            return json.dumps({"action": "list_tasks", "args": {"sort_by": sort_by, "overdue_only": overdue_only}}, ensure_ascii=False)
        return '{"action": "list_tasks", "args": {}}'

    if any(w in user_input for w in ["统计", "状态", "总结", "进度"]):
        return '{"action": "get_stats", "args": {}}'

    if any(w in user_input for w in ["搜索", "查找", "找", "包含"]):
        keyword = user_input
        for w in ["搜索", "查找", "找一下", "帮我找", "包含"]:
            keyword = keyword.replace(w, "", 1)
        keyword = keyword.strip().strip("的。！\"\"''")
        if not keyword:
            keyword = user_input.strip()
        return json.dumps({"action": "search_tasks", "args": {"keyword": keyword}}, ensure_ascii=False)

    if any(w in user_input for w in ["导出", "保存为", "输出"]):
        return json.dumps({"action": "export_csv", "args": {"filepath": "tasks_export.csv"}}, ensure_ascii=False)

    # 无法识别
    return '{"action": "unknown", "args": {"raw": "' + user_input + '"}}'


# ── parse_model_output ─────────────────────────────────────

def parse_model_output(model_output):
    """解析模型输出的 JSON 字符串，返回 (action_name, args) 元组。"""
    try:
        data = json.loads(model_output)
        return data["action"], data.get("args", {})
    except (json.JSONDecodeError, KeyError):
        return "unknown", {"raw": model_output}


# ── guardrail ──────────────────────────────────────────────

def guardrail(action, args):
    """安全检查：拦截危险操作，返回 (allowed, reason) 元组。"""
    if action == "delete_all_tasks":
        return False, "批量删除操作需要人工确认。请确认后使用 delete <id> 逐个删除。"
    if action == "unknown":
        return False, "无法识别的操作。"
    if action not in AVAILABLE_ACTIONS:
        return False, f"未知操作类型: {action}"
    return True, "ok"


# ── execute_tool ───────────────────────────────────────────

def execute_tool(action, args):
    """执行已通过安全检查的操作，调用 CampusTask 业务函数。"""
    from campus_task import task_manager as tm

    if action == "add_task":
        task = tm.add_task(
            args.get("title", ""),
            deadline=args.get("deadline"),
            priority=args.get("priority"),
        )
        return f"已添加任务 [{task['id']}]: {task['title']}"

    elif action == "list_tasks":
        tasks = tm.list_tasks(
            status_filter=args.get("status_filter"),
            sort_by=args.get("sort_by"),
            overdue_only=args.get("overdue_only", False),
        )
        if not tasks:
            label = "逾期" if args.get("overdue_only") else ""
            return f"暂无{label}任务。" if label else "暂无任务。"
        lines = []
        for t in tasks:
            mark = "[x]" if t["status"] == "done" else "[ ]"
            line = f"[{mark}] {t['id']}. {t['title']}"
            if t.get("deadline"):
                line += f" (截止: {t['deadline']})"
            if t.get("priority"):
                line += f" [{t['priority']}]"
            lines.append(line)
        return "\n".join(lines)

    elif action == "done_task":
        success, msg = tm.done_task(args["task_id"])
        return msg

    elif action == "delete_task":
        success, msg = tm.delete_task(args["task_id"])
        return msg

    elif action == "search_tasks":
        results = tm.search_tasks(args["keyword"])
        if not results:
            return f"未找到包含 '{args['keyword']}' 的任务。"
        return f"找到 {len(results)} 条: " + ", ".join(t["title"] for t in results)

    elif action == "get_stats":
        stats = tm.get_stats()
        return f"总 {stats['total']} 个任务，已完成 {stats['done']}，待办 {stats['todo']}"

    elif action == "export_csv":
        count = tm.export_csv(args["filepath"])
        return f"已导出 {count} 条任务到 {args['filepath']}"

    return f"未知操作: {action}"


# ── write_trace ────────────────────────────────────────────

def write_trace(event):
    """将追踪事件追加写入 trace.jsonl。"""
    event["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("trace.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── run_harness ────────────────────────────────────────────

def run_harness(user_input):
    """完整的 AI Harness 处理管线：用户输入 → 执行 → 追踪。

    返回 (success, result_message) 元组。
    """
    from campus_task.storage import load_tasks

    tasks_state = load_tasks()

    # Step 1: 构建提示词
    prompt = prompt_builder(user_input, tasks_state)

    # Step 2: 调用模型（模拟）
    model_output = mock_model(prompt)

    # Step 3: 解析输出
    action, args = parse_model_output(model_output)

    # Step 4: 安全检查
    allowed, reason = guardrail(action, args)

    event = {
        "user_input": user_input,
        "prompt": prompt,
        "model_output": model_output,
        "action": action,
        "args": args,
        "allowed": allowed,
        "reason": reason,
    }

    if not allowed:
        event["result"] = "blocked"
        write_trace(event)
        return False, f"[guardrail] {reason}"

    # Step 5: 执行工具
    try:
        result_msg = execute_tool(action, args)
        event["result"] = result_msg
        write_trace(event)
        return True, result_msg
    except Exception as e:
        event["result"] = f"error: {str(e)}"
        write_trace(event)
        return False, f"[error] {str(e)}"


# ── run_eval ───────────────────────────────────────────────

def run_eval(eval_file="eval_cases.json"):
    """运行评估：逐条执行测试用例，计算准确率。"""
    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    # 清空之前的数据
    from campus_task.storage import TASKS_FILE, save_tasks
    save_tasks([])

    # 清空 trace
    with open("trace.jsonl", "w", encoding="utf-8") as f:
        f.write("")

    passed = 0
    for i, case in enumerate(cases):
        user_input = case["input"]
        expected_action = case["expected_action"]

        prompt = prompt_builder(user_input, [])
        model_output = mock_model(prompt)
        action, args = parse_model_output(model_output)
        allowed, _ = guardrail(action, args)

        actual_action = action if allowed else "blocked"

        status = "PASS" if actual_action == expected_action else "FAIL"
        if status == "PASS":
            passed += 1

        print(f"  Case {i + 1:02d}: \"{user_input}\"")
        print(f"    expected={expected_action}  actual={action}  -> {status}")

    accuracy = passed / len(cases)
    print(f"\n{len(cases)} cases, {passed} passed, accuracy={accuracy:.2f}")
    return accuracy


if __name__ == "__main__":
    # 演示模式
    print("=== AI Harness 演示 ===\n")

    demos = [
        "添加一个社交关系分析实验报告",
        "列出我所有未完成的任务",
        "把第2个任务标记为完成",
        "删除第3个任务",
        "删除所有任务",  # 应被 guardrail 拦截
    ]

    for d in demos:
        print(f"> {d}")
        success, msg = run_harness(d)
        print(f"  {'[OK]' if success else '[FAIL]'} {msg}\n")

    print("=== 评估模式 ===")
    run_eval()
