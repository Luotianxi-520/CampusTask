# Changelog

All notable changes to CampusTask are documented in this file.

## [0.2.1] — 2026-06-12

### Fixed
- 修复：`tasks.json` 为空文件时程序崩溃 → 现在返回空列表，记录警告日志

### Added
- 日志系统：操作日志写入 `campus_task.log`（JSON 读写、任务增删等）
- `test_load_empty_file`：验证空文件不崩溃

### Changed
- `load_tasks()` 增加了空内容显式检查（`if not content.strip()`）

## [0.2.0] — 2026-06-12

### Added
- `--version` 参数（显示版本号）
- `--help` 参数（argparse 自动生成的完整帮助）
- 可安装包结构（`campus_task/` 目录，支持 `python -m campus_task`）
- `pyproject.toml` 包配置
- `USER_GUIDE.md` 用户手册

### Changed
- CLI 从手动 `sys.argv` 解析迁移为 `argparse`
- 内部导入改为相对导入
- 版本格式：YYYY-MM-DD → YYYY-MM-DD HH:MM:SS

## [0.1.1] — 2026-06-12

### Added
- CSV 导出功能（`export` 命令）
- 按截止日期排序（`list --sort deadline`）
- 40 个测试用例

## [0.1.0] — 2026-06-12

### Added
- 初始版本：`add`, `list`, `done`, `delete`, `search`, `stats` 命令
- pytest 测试套件（35 个测试）
- `deadline` 和 `priority` 字段
- 状态过滤和标题编辑
