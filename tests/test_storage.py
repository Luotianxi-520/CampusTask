"""测试 storage 模块：JSON 文件读写、异常处理。"""

import json
import os

import pytest

import storage


def test_load_tasks_file_not_exists(tmp_path, monkeypatch):
    """JSON 文件不存在时，load_tasks 返回空列表。"""
    nonexistent = str(tmp_path / "nonexistent.json")
    monkeypatch.setattr(storage, "TASKS_FILE", nonexistent)

    tasks = storage.load_tasks()
    assert tasks == []


def test_save_and_load_tasks(tmp_path, monkeypatch):
    """保存任务后重新加载，数据一致。"""
    test_file = str(tmp_path / "test_tasks.json")
    monkeypatch.setattr(storage, "TASKS_FILE", test_file)

    sample = [
        {"id": 1, "title": "Test", "status": "todo", "created_at": "2026-01-01 12:00:00"}
    ]
    storage.save_tasks(sample)
    loaded = storage.load_tasks()

    assert loaded == sample
    assert loaded[0]["title"] == "Test"


def test_load_corrupt_json(tmp_path, monkeypatch):
    """JSON 文件格式损坏时，友好报错并返回空列表。"""
    corrupt_file = str(tmp_path / "corrupt.json")
    with open(corrupt_file, "w", encoding="utf-8") as f:
        f.write("this is not valid json{{{")

    monkeypatch.setattr(storage, "TASKS_FILE", corrupt_file)
    tasks = storage.load_tasks()

    assert tasks == []


def test_save_tasks_creates_file(tmp_path, monkeypatch):
    """save_tasks 在文件不存在时自动创建。"""
    test_file = str(tmp_path / "new_file.json")
    monkeypatch.setattr(storage, "TASKS_FILE", test_file)

    assert not os.path.exists(test_file)
    storage.save_tasks([{"id": 1, "title": "New", "status": "todo", "created_at": ""}])
    assert os.path.exists(test_file)

    with open(test_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
