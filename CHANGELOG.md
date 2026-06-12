# Changelog

All notable changes to CampusTask are documented in this file.

## [0.3.0] — 2026-06-12

### Added
- `export_csv(filepath)` — export all tasks to CSV format
- `list_tasks(sort_by="deadline")` — sort task list by deadline (ascending, tasks without deadline at end)
- CLI: `python main.py export <filepath>` command
- CLI: `python main.py list --sort deadline` option
- Test cases for CSV export (empty and populated) and deadline sorting

## [0.2.0] — 2026-06-12

### Added
- `deadline` field — optional deadline date (YYYY-MM-DD)
- `priority` field — optional priority label (high / medium / low)
- `edit_task(task_id, new_title)` — modify task title
- `list_tasks(status_filter)` — filter by todo/done status
- CLI: `--deadline`, `--priority` options for `add` command
- CLI: `--status` option for `list` command
- CLI: `edit <id> <new_title>` command

## [0.1.0] — 2026-06-12

### Added
- pytest test suite: 22 test cases covering core functions and edge cases
- `test_storage.py`: file persistence, corrupt JSON handling
- `test_task_manager.py`: add/list/done/delete/search/stats/id management
- Empty title validation (ValueError)
- Corrupt JSON recovery (returns empty list)

## [0.0.1] — 2026-06-12

### Added
- CLI task manager: `add`, `list`, `done`, `delete`, `search`, `stats` commands
- Modular architecture: `storage.py` / `task_manager.py` / `cli.py` / `main.py`
- JSON file persistence (`tasks.json`)
- Auto-incrementing task IDs
