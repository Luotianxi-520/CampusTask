"""测试 task_manager 模块：业务逻辑（增删改查）和边界条件。"""

import os

import pytest

import task_manager
import storage


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """每个测试用例使用独立的临时 JSON 文件，避免相互影响。"""
    test_file = str(tmp_path / "test_tasks.json")
    monkeypatch.setattr(storage, "TASKS_FILE", test_file)


# ── add_task ──────────────────────────────────────────────

def test_add_task_success():
    """添加任务成功，返回任务对象且已持久化。"""
    task = task_manager.add_task("提交数字电路实验报告")

    assert task["id"] == 1
    assert task["title"] == "提交数字电路实验报告"
    assert task["status"] == "todo"
    assert "created_at" in task

    tasks = storage.load_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "提交数字电路实验报告"


def test_add_task_empty_title():
    """添加空标题任务时应拒绝并抛出 ValueError。"""
    with pytest.raises(ValueError, match="任务标题不能为空"):
        task_manager.add_task("")


def test_add_task_whitespace_title():
    """添加纯空白标题也应拒绝。"""
    with pytest.raises(ValueError, match="任务标题不能为空"):
        task_manager.add_task("   ")


# ── list_tasks ────────────────────────────────────────────

def test_list_empty():
    """无任务时返回空列表。"""
    tasks = task_manager.list_tasks()
    assert tasks == []


def test_list_with_tasks():
    """添加多个任务后，列表包含全部任务。"""
    task_manager.add_task("任务A")
    task_manager.add_task("任务B")
    task_manager.add_task("任务C")

    tasks = task_manager.list_tasks()
    assert len(tasks) == 3
    assert [t["title"] for t in tasks] == ["任务A", "任务B", "任务C"]


def test_list_filter_todo():
    """按状态过滤 — 只显示待办任务。"""
    task_manager.add_task("待办A")
    task_manager.add_task("待办B")
    task_manager.done_task(2)

    tasks = task_manager.list_tasks(status_filter="todo")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "待办A"


def test_list_filter_done():
    """按状态过滤 — 只显示已完成任务。"""
    task_manager.add_task("完成A")
    task_manager.done_task(1)

    tasks = task_manager.list_tasks(status_filter="done")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "完成A"


def test_list_filter_none():
    """不传 filter 时返回全部任务。"""
    task_manager.add_task("任务1")
    task_manager.add_task("任务2")
    task_manager.done_task(1)

    tasks = task_manager.list_tasks()
    assert len(tasks) == 2


# ── done_task ─────────────────────────────────────────────

def test_done_existing_task():
    """完成存在的任务返回 success=True 并更新状态。"""
    task_manager.add_task("复习高数")
    success, msg = task_manager.done_task(1)

    assert success is True
    assert "已标记为完成" in msg

    tasks = storage.load_tasks()
    assert tasks[0]["status"] == "done"


def test_done_nonexistent_task():
    """完成不存在的任务返回 success=False。"""
    success, msg = task_manager.done_task(999)

    assert success is False
    assert "不存在" in msg


def test_done_already_done_task():
    """重复标记已完成任务应提示。"""
    task_manager.add_task("已完成的任务")
    task_manager.done_task(1)
    success, msg = task_manager.done_task(1)

    assert success is False
    assert "已经是完成状态" in msg


# ── delete_task ───────────────────────────────────────────

def test_delete_existing_task():
    """删除存在的任务，返回 success=True，JSON 中移除。"""
    task_manager.add_task("待删除任务")
    success, msg = task_manager.delete_task(1)

    assert success is True
    assert "已删除" in msg
    assert len(storage.load_tasks()) == 0


def test_delete_nonexistent_task():
    """删除不存在的任务返回 success=False。"""
    success, msg = task_manager.delete_task(999)

    assert success is False
    assert "不存在" in msg


# ── edit_task ────────────────────────────────────────────

def test_edit_existing_task():
    """修改存在任务的标题。"""
    task_manager.add_task("原标题")
    success, msg = task_manager.edit_task(1, "新标题")

    assert success is True
    assert "已更新" in msg
    tasks = storage.load_tasks()
    assert tasks[0]["title"] == "新标题"


def test_edit_nonexistent_task():
    """修改不存在任务返回 success=False。"""
    success, msg = task_manager.edit_task(999, "新标题")

    assert success is False
    assert "不存在" in msg


def test_edit_empty_title():
    """修改为空标题时抛出 ValueError。"""
    task_manager.add_task("任务")
    with pytest.raises(ValueError, match="任务标题不能为空"):
        task_manager.edit_task(1, "")


def test_edit_whitespace_title():
    """修改为纯空白标题时抛出 ValueError。"""
    task_manager.add_task("任务")
    with pytest.raises(ValueError, match="任务标题不能为空"):
        task_manager.edit_task(1, "   ")


# ── ID 管理 ───────────────────────────────────────────────

def test_id_auto_increment():
    """新增任务时编号自动递增。"""
    t1 = task_manager.add_task("任务1")
    t2 = task_manager.add_task("任务2")
    t3 = task_manager.add_task("任务3")

    assert t1["id"] == 1
    assert t2["id"] == 2
    assert t3["id"] == 3


def test_id_no_reuse_after_delete():
    """删除任务后新增任务不重用已删除编号。"""
    task_manager.add_task("任务1")   # id=1
    task_manager.add_task("任务2")   # id=2
    task_manager.delete_task(1)      # 删除 id=1
    t3 = task_manager.add_task("任务3")

    assert t3["id"] == 3  # 基于历史最大值 2 + 1


# ── 持久化 ────────────────────────────────────────────────

def test_persistence_round_trip():
    """保存后重新加载，数据完整一致。"""
    task_manager.add_task("测试持久化")
    task_manager.done_task(1)

    reloaded = storage.load_tasks()
    assert len(reloaded) == 1
    assert reloaded[0]["title"] == "测试持久化"
    assert reloaded[0]["status"] == "done"


# ── search_tasks ──────────────────────────────────────────

def test_search_exact_match():
    """精确关键词搜索。"""
    task_manager.add_task("软件工程实验报告")
    task_manager.add_task("高等数学作业")

    results = task_manager.search_tasks("软件工程")
    assert len(results) == 1
    assert results[0]["title"] == "软件工程实验报告"


def test_search_case_insensitive():
    """搜索不区分大小写。"""
    task_manager.add_task("ABCdef")
    results = task_manager.search_tasks("abcdef")
    assert len(results) == 1


def test_search_no_match():
    """无匹配任务时返回空列表。"""
    task_manager.add_task("任务一")
    results = task_manager.search_tasks("不存在的关键词")
    assert results == []


# ── get_stats ─────────────────────────────────────────────

def test_stats_empty():
    """无任务时统计全为 0。"""
    stats = task_manager.get_stats()
    assert stats == {"total": 0, "done": 0, "todo": 0}


def test_stats_with_mixed_tasks():
    """混合状态任务统计正确。"""
    task_manager.add_task("任务1")
    task_manager.add_task("任务2")
    task_manager.add_task("任务3")
    task_manager.done_task(1)
    task_manager.done_task(3)

    stats = task_manager.get_stats()
    assert stats["total"] == 3
    assert stats["done"] == 2
    assert stats["todo"] == 1


# ── deadline ─────────────────────────────────────────────

def test_add_task_with_deadline():
    """添加带截止日期的任务。"""
    task = task_manager.add_task("提交实验报告", deadline="2026-06-30")
    assert task["deadline"] == "2026-06-30"


def test_add_task_without_deadline():
    """不提供截止日期时，任务不含 deadline 字段。"""
    task = task_manager.add_task("无截止日期任务")
    assert "deadline" not in task


def test_persistence_with_deadline():
    """带 deadline 的任务持久化后数据一致。"""
    task_manager.add_task("有截止日期", deadline="2026-12-31")
    reloaded = storage.load_tasks()
    assert reloaded[0]["deadline"] == "2026-12-31"


# ── priority ─────────────────────────────────────────────

def test_add_task_with_priority():
    """添加带优先级的任务。"""
    task = task_manager.add_task("紧急任务", priority="high")
    assert task["priority"] == "high"


def test_add_task_without_priority():
    """不提供优先级时，任务不含 priority 字段。"""
    task = task_manager.add_task("普通任务")
    assert "priority" not in task


def test_persistence_with_priority():
    """带 priority 的任务持久化后数据一致。"""
    task_manager.add_task("高优先级", priority="high")
    reloaded = storage.load_tasks()
    assert reloaded[0]["priority"] == "high"


# ── sort_by ─────────────────────────────────────────────

def test_sort_by_deadline():
    """按截止日期排序，有 deadline 的升序在前，无 deadline 的在后。"""
    task_manager.add_task("无日期")
    task_manager.add_task("晚截止", deadline="2026-12-31")
    task_manager.add_task("早截止", deadline="2026-01-15")

    tasks = task_manager.list_tasks(sort_by="deadline")
    assert tasks[0]["deadline"] == "2026-01-15"
    assert tasks[1]["deadline"] == "2026-12-31"
    assert "deadline" not in tasks[2]  # 无日期的排最后


def test_sort_mixed_with_filter():
    """排序 + 过滤组合使用。"""
    task_manager.add_task("待办A", deadline="2026-06-01")
    task_manager.add_task("待办B", deadline="2026-03-01")
    task_manager.add_task("已完成", deadline="2026-01-01")
    task_manager.done_task(3)

    tasks = task_manager.list_tasks(status_filter="todo", sort_by="deadline")
    assert len(tasks) == 2
    assert tasks[0]["deadline"] == "2026-03-01"
    assert tasks[1]["deadline"] == "2026-06-01"


# ── export_csv ──────────────────────────────────────────

def test_export_csv_empty(tmp_path):
    """无任务时导出空 CSV（仅含表头）。"""
    filepath = str(tmp_path / "empty.csv")
    count = task_manager.export_csv(filepath)
    assert count == 0
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()
    assert "id,title,status,created_at,deadline,priority" in content


def test_export_csv_with_tasks(tmp_path):
    """导出包含多条任务的 CSV。"""
    task_manager.add_task("任务A", deadline="2026-06-01", priority="high")
    task_manager.add_task("任务B")
    filepath = str(tmp_path / "tasks.csv")

    count = task_manager.export_csv(filepath)
    assert count == 2

    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    assert len(lines) == 3  # header + 2 tasks
    assert "任务A" in lines[1]
    assert "2026-06-01" in lines[1]
    assert "high" in lines[1]
    assert "任务B" in lines[2]
