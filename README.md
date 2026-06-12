# CampusTask — 自动化测试（pytest）

为 CampusTask 模块化版本编写 22 个自动化测试用例，覆盖核心功能和边界条件。

## 项目结构

```
实验三/
├── main.py              # 程序入口
├── cli.py               # 命令行接口
├── task_manager.py      # 业务逻辑（含空标题校验）
├── storage.py           # JSON 持久化（含损坏文件处理）
├── tests/
│   ├── __init__.py
│   ├── test_storage.py      # 4 个存储层测试
│   └── test_task_manager.py # 18 个业务逻辑测试
├── .venv/               # 虚拟环境
└── README.md
```

## 运行测试

```bash
cd 实验三
python -m venv .venv
.venv/Scripts/pip install pytest
.venv/Scripts/python -m pytest tests/ -v
```

## 测试用例清单

### test_storage.py（存储层 — 4 个）

| # | 测试 | 覆盖场景 |
|---|------|----------|
| 1 | test_load_tasks_file_not_exists | JSON 文件不存在 → 返回空列表 |
| 2 | test_save_and_load_tasks | 保存后重新加载 → 数据一致 |
| 3 | test_load_corrupt_json | JSON 格式损坏 → 返回空列表 |
| 4 | test_save_tasks_creates_file | 保存时自动创建文件 |

### test_task_manager.py（业务层 — 18 个）

| # | 测试 | 覆盖场景 |
|---|------|----------|
| 5 | test_add_task_success | 正常添加任务 |
| 6 | test_add_task_empty_title | 空字符串 → ValueError |
| 7 | test_add_task_whitespace_title | 纯空白 → ValueError |
| 8 | test_list_empty | 无任务返回空列表 |
| 9 | test_list_with_tasks | 多任务列表正确 |
| 10 | test_done_existing_task | 完成存在的任务 |
| 11 | test_done_nonexistent_task | 完成不存在的任务 |
| 12 | test_done_already_done_task | 重复完成已完成任务 |
| 13 | test_delete_existing_task | 删除存在的任务 |
| 14 | test_delete_nonexistent_task | 删除不存在的任务 |
| 15 | test_id_auto_increment | ID 自动递增 |
| 16 | test_id_no_reuse_after_delete | 删除后不重用编号 |
| 17 | test_persistence_round_trip | 保存→加载数据完整 |
| 18 | test_search_exact_match | 精确关键词搜索 |
| 19 | test_search_case_insensitive | 搜索不区分大小写 |
| 20 | test_search_no_match | 无匹配返回空 |
| 21 | test_stats_empty | 空数据统计 |
| 22 | test_stats_with_mixed_tasks | 混合状态统计 |

## Bug 修复流程

按要求"先引入 bug → 测试失败 → 修复 → 重测通过"：

### Bug 1：空标题未校验

**初始状态**：`task_manager.add_task("")` 可以成功创建空标题任务。

**失败测试**（首次运行）：
```
FAILED tests/test_task_manager.py::test_add_task_empty_title
FAILED tests/test_task_manager.py::test_add_task_whitespace_title
```

**修复**：`task_manager.py:14-16` — 在 `add_task()` 开头添加：
```python
if not title or not title.strip():
    raise ValueError("任务标题不能为空")
```

### Bug 2：损坏 JSON 直接崩溃

**初始状态**：`tasks.json` 被手动破坏后，`load_tasks()` 抛出 `JSONDecodeError` 导致程序崩溃。

**失败测试**（首次运行）：
```
FAILED tests/test_storage.py::test_load_corrupt_json
```

**修复**：`storage.py:13-16` — 用 `try/except json.JSONDecodeError` 包裹：
```python
try:
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
except json.JSONDecodeError:
    return []
```

### 修复后结果

```
22 passed in 0.32s
```

## 实验反思

**问题：为什么测试要在编码之前？**

测试不是"写完代码后再补的证明"，而是"写代码前先定的合同"。

在实验三中这个过程很清晰：先写测试用例，明确"空标题必须抛异常"、"损坏 JSON 必须返回空列表"，然后运行 → 失败 → 修复代码 → 通过。测试充当了需求的精确表达——`pytest.raises(ValueError, match="任务标题不能为空")` 比口头描述"应该拒绝空标题"更精确且不可误解。

实际工程中，如果没有测试，修复 bug 时无法确认：
- 修复真的有效（而不是碰巧不报错了）
- 修复没有引入新 bug（已有测试会告诉你）

22 个测试在 0.32 秒内跑完，每一次代码改动都能立刻知道是否破坏了已有功能——这就是安全网的价值。

**为什么 `isolate_storage` 是必须的？**

每个测试使用独立的临时 JSON 文件（`tmp_path` + `monkeypatch`），测试之间互不干扰。如果不隔离，测试的执行顺序会影响结果（一个测试的残留数据会导致另一个测试意外通过或失败），让测试变得不可靠。可靠的测试必须是确定性的：给定相同代码，每次运行结果相同。
