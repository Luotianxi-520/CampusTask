# CampusTask — 发布与维护

将 CampusTask 打包为可安装的 Python 包，模拟真实场景中的 bug 修复和版本发布。

## 项目结构

```
CampusTask/
├── campus_task/                  # 可安装的 Python 包
│   ├── __init__.py               # 包初始化 + 日志配置 + 版本号
│   ├── __main__.py               # python -m campus_task 入口
│   ├── cli.py                    # 命令行接口（argparse）
│   ├── task_manager.py           # 业务逻辑
│   └── storage.py                # JSON 持久化 + 日志
├── tests/
│   ├── test_storage.py           # 5 个存储测试（含空文件）
│   └── test_task_manager.py      # 35 个业务测试
├── main.py                       # 备用入口
├── pyproject.toml                # 包元数据与构建配置
├── .github/workflows/test.yml    # CI 配置
├── USER_GUIDE.md                 # 用户手册
├── CHANGELOG.md                  # 版本记录
└── README.md
```

## 安装与使用

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e .

# 以包方式运行
python -m campus_task --version    # campus-task 0.2.1
python -m campus_task --help       # 完整帮助
python -m campus_task add "任务" --deadline 2026-06-30 --priority high
python -m campus_task list --sort deadline
python -m campus_task export tasks.csv

# 也支持旧的入口方式
python main.py add "任务"
```

## 本版本新增功能（v0.2.1）

| 功能 | 说明 |
|------|------|
| `--version` | 显示版本号 `campus-task 0.2.1` |
| `--help` | argparse 自动生成的完整帮助，含所有子命令说明 |
| 日志系统 | 操作日志记录到 `campus_task.log` |
| 空文件修复 | `tasks.json` 为空时不再崩溃，返回空列表 |

## Bug 修复记录

### Bug 报告：tasks.json 为空文件时程序崩溃

**来源**：用户反馈

**复现步骤**：
1. 创建一个空文件 `echo "" > tasks.json`
2. 运行 `python -m campus_task add "test"`
3. 程序抛出 `JSONDecodeError` 退出

**根因分析**：`storage.load_tasks()` 检测到文件存在后直接调用 `json.loads()`，空字符串不是合法 JSON，触发 `JSONDecodeError`。原有的 `except` 虽然捕获了，但空文件应该被视为"没有数据"而非"格式损坏"。

**修复方案**（`storage.py`）：
```python
content = f.read()
if not content.strip():          # 新增：显式处理空文件
    logger.warning("tasks.json 存在但为空，视为空列表。")
    return []
return json.loads(content)       # 原来直接调用，现在先读再解析
```

**验证测试**（`tests/test_storage.py::test_load_empty_file`）：
```python
def test_load_empty_file(tmp_path, monkeypatch):
    empty_file = str(tmp_path / "empty.json")
    with open(empty_file, "w", encoding="utf-8") as f:
        f.write("")
    monkeypatch.setattr(storage, "TASKS_FILE", empty_file)
    tasks = storage.load_tasks()
    assert tasks == []
```

**修复后验证**：
```
.venv/Scripts/python -m pytest tests/ -v
# 40 passed in 0.81s
```

## 日志示例

```
2026-06-12 15:02:04 [INFO] campus_task.task_manager: 添加任务 [1]: 提交实验
2026-06-12 15:02:04 [INFO] campus_task: 已保存 1 条任务到 tasks.json
```

## 运行测试

```bash
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m pytest tests/ -v
# 40 passed in 0.81s
```

## 实验反思

**问题：为什么维护阶段比初次开发更昂贵？**

本次实验修改了 `storage.py` 的一处逻辑（显式检查空内容），但为此需要：

1. **定位问题**：理解用户报告，确定触发条件
2. **写测试**：新增 `test_load_empty_file` 验证修复
3. **跑全部测试**：确认修复没有破坏已有功能（40 个测试）
4. **更新文档**：CHANGELOG.md 记录修复，更新版本号
5. **发布**：提交代码，推送到仓库

维护成本高的原因：
- **上下文成本**：修复者可能是几周后回来看代码的人，需要重新理解模块的输入输出约定
- **回归风险**：修复一个 bug 可能引入另一个。本例中 40 个测试全部通过才敢合并——没有测试的代码维护几乎是"盲修"
- **文档同步**：代码变了，文档也必须同步更新，否则下一个维护者面临代码与文档不一致的困惑

这也解释了为什么规范的项目必须同时交付"可运行的代码"和"可验证的测试"两样东西。
