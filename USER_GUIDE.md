# CampusTask 用户手册

## 安装

```bash
# 克隆仓库后，进入项目目录
python -m venv .venv
.venv/Scripts/python -m pip install -e .
```

## 快速开始

```bash
# 查看版本
python -m campus_task --version

# 查看帮助
python -m campus_task --help

# 添加任务
python -m campus_task add "复习高等数学"

# 添加带截止日期和优先级的任务
python -m campus_task add "提交实验报告" --deadline 2026-06-30 --priority high

# 查看所有任务
python -m campus_task list

# 按截止日期排序
python -m campus_task list --sort deadline

# 只看待办任务
python -m campus_task list --status todo

# 完成任务
python -m campus_task done 1

# 删除任务
python -m campus_task delete 1

# 修改任务标题
python -m campus_task edit 1 "修改后的标题"

# 搜索任务
python -m campus_task search "实验"

# 统计
python -m campus_task stats

# 导出 CSV
python -m campus_task export tasks.csv
```

## 命令参考

### `add` — 添加任务

```
python -m campus_task add <标题> [--deadline YYYY-MM-DD] [--priority high|medium|low]
```

- `标题`：必填，不能为空
- `--deadline`：可选，截止日期
- `--priority`：可选，优先级（high / medium / low）

### `list` — 查看任务

```
python -m campus_task list [--status todo|done] [--sort deadline]
```

- `--status`：按状态过滤
- `--sort deadline`：按截止日期升序排列（无截止日期的排最后）

### `done` — 标记完成

```
python -m campus_task done <任务编号>
```

### `delete` — 删除任务

```
python -m campus_task delete <任务编号>
```

### `edit` — 修改标题

```
python -m campus_task edit <任务编号> <新标题>
```

### `search` — 搜索

```
python -m campus_task search <关键词>
```

支持模糊搜索，不区分大小写。

### `export` — 导出 CSV

```
python -m campus_task export <文件路径>
```

导出的 CSV 文件使用 UTF-8 BOM 编码，可直接用 Excel 打开。

### `stats` — 统计

```
python -m campus_task stats
```

显示总任务数、已完成数、待办数。

## 数据存储

任务数据存储在 `tasks.json` 中。如果文件不存在，程序会自动创建。

## 日志

运行日志记录在 `campus_task.log` 中，包含操作时间和结果。

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 1 | 发生错误（无效输入、操作失败等） |
