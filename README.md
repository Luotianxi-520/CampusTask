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

## AI Harness 架构

```
用户自然语言输入
       │
       ▼
┌─────────────────┐
│ prompt_builder   │  根据当前任务状态构造上下文提示词
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  mock_model      │  规则匹配：将自然语言映射为 JSON 操作指令
│  (可替换为LLM)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ parse_model_output│ 解析 JSON → (action, args)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   guardrail      │  安全检查：拦截批量删除等危险操作
│ (human-in-loop)  │
└────────┬────────┘
         │ allowed=true
         ▼
┌─────────────────┐
│  execute_tool    │  调用 CampusTask 业务函数执行操作
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  write_trace     │  全程事件写入 trace.jsonl 审计日志
└─────────────────┘

             ┌─────────────────┐
             │   run_eval      │  评测模式：用例集 → 准确率
             │ (eval_cases.json)│
             └─────────────────┘
```

**管线原则**：
- 每个环节独立、可替换。mock_model 可随时替换为真实 LLM API，其余环节不变
- guardrail 是安全阀门——模型输出不可靠，必须在执行前进行规则校验
- trace 提供完整审计链：用户输入 → prompt → 模型输出 → 决策 → 结果

## AI Harness 反思报告

**题目：为什么现在的 AI harness 工程像软件工程？哪些工作仍由人写代码完成，哪些工作交给了模型？当模型可能出错时，需求、测试、日志、权限和人工审批为什么反而更重要？**

在构建 CampusTask 的 AI harness 过程中，我发现一个核心事实：AI harness 工程本质上仍然是软件工程，只是系统中有一个组件——"意图识别"——从确定性代码变成了概率性模型输出。

**模型做什么，人做什么？**

在这个系统中，模型（mock_model）只做一件事：将用户的自然语言输入映射为一个结构化的操作指令（JSON）。它负责"理解意图"——用户说"帮我添加一个明天交的报告"，模型输出 `{"action": "add_task", "args": {"title": "报告", "deadline": "2026-06-13"}}`。

剩下的所有工作仍然由人写的确定性代码完成：prompt_builder 构造上下文提示词，定义了模型需要哪些信息、输出什么格式；parse_model_output 解析模型输出，处理 JSON 解析失败的情况；guardrail 检查操作是否危险——"删除所有任务"会被拦截，不是因为模型没理解，而是因为规则明确禁止；execute_tool 调用已有的 CampusTask 业务函数，这些函数自身有输入校验和错误处理；write_trace 记录全过程的审计日志，确保任何决策都可追溯。

模型只替换了"从自然语言到指令"这一步。它没有替换数据存储、业务逻辑、权限控制、日志审计——这些仍然是软件工程的核心。

**为什么模型不可靠时，工程纪律更重要？**

模型可能出错——这是 AI harness 工程的前提假设。mock_model 基于规则匹配，效果有限；真实 LLM 可能产生幻觉，输出不存在的 action 或错误的参数。正因为输出不可靠，围绕它的工程措施反而必须更严格。

需求：必须明确定义"模型能做什么、不能做什么"。AVAILABLE_ACTIONS 字典就是一份能力边界合同——模型只能请求这里面的操作，超出范围的操作在 guardrail 层被拒绝。这不是限制模型，而是定义系统的安全范围。

测试：eval_cases.json 中的 10+ 条用例不是测试模型是否"聪明"，而是测试管线是否正确处理了模型的输出。一条用例 `{"input": "删除所有任务", "expected_action": "blocked"}` 验证的是 guardrail 的拦截能力，与模型无关。当 mock_model 替换为真实 LLM 后，这些用例依然是安全网。

日志：trace.jsonl 记录的不是"模型推理过程"，而是"系统决策链"。当系统做出错误操作时，trace 能告诉你：用户说了什么 → 模型理解成了什么 → 系统放行了还是拦截了。没有 trace，AI 系统就是一个黑箱；有了 trace，它和传统软件一样可调试。

权限与人工审批：guardrail 体现了 human-in-the-loop 思想。批量删除操作不是技术上行不通——模型完全可以生成 `delete_all_tasks`——而是工程上不允许。这和传统系统中"sudo 需要二次确认"是同一个逻辑：不是机器做不到，而是人必须对高风险操作负责。

**与软件工程的相似性**

AI harness 的每个组件都能在传统软件工程中找到对应：prompt_builder 是"接口定义"，定义了模型的输入契约；AVAILABLE_ACTIONS 是"能力清单"，类似 API 的 OpenAPI spec；guardrail 是"权限中间件"，类似 Web 应用的 auth middleware；trace 是"审计日志"，类似数据库的 WAL 或应用的操作日志；run_eval 是"测试套件"，只是测试的对象从函数返回值变成了模型意图分类的准确率。

区别在于，传统软件中"意图识别"也是确定性代码（if-else 或正则），而 AI harness 中这一步交给了模型。但围绕它的工程实践——需求、设计、测试、日志、权限、维护——不仅没有消失，反而因为模型的不确定性而变得更加必要。

**结论**

AI harness 工程不会让软件工程过时，它只是把"意图理解"这一层从确定性代码替换为概率模型。替换之后，软件工程的质量保障手段——需求的精确性、测试的覆盖率、日志的可追溯性、权限的最小化原则、人工审批的兜底机制——比以往任何时候都更加重要。因为当系统中有一个"不可靠但有能力"的组件时，保守的工程纪律是唯一的保险。

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
