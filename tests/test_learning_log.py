"""第3回 演習（make_quiz）と宿題（save_learning_log と承認）のテスト（APIキー不要）。"""

import json

import pytest
from pydantic_ai import DeferredToolRequests
from pydantic_ai.models.test import TestModel

from app import tools
from app.agent import agent, run_with_approval


@pytest.fixture
def log_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path / "learning_log")
    return tmp_path / "learning_log"


def test_make_quiz_uses_term_of_the_lecture():
    quiz = json.loads(tools.make_quiz(2))
    terms = {e["term"]: e["definition"] for e in tools.load_glossary() if e["lecture"] == 2}
    name = quiz["question"].removeprefix("「").removesuffix("」の意味は？")
    assert terms[name] == quiz["answer"]


def test_make_quiz_reports_missing_lecture():
    assert "error" in json.loads(tools.make_quiz(0))


def test_save_learning_log_writes_markdown(log_dir):
    message = tools.save_learning_log("LoRAのまとめ", "重みを固定して差分だけ学習する")
    files = list(log_dir.glob("*.md"))
    assert len(files) == 1 and files[0].name in message
    assert "重みを固定して差分だけ学習する" in files[0].read_text(encoding="utf-8")


def test_save_learning_log_stays_in_folder(log_dir):
    tools.save_learning_log("../../etc/passwd", "本文")
    files = list(log_dir.glob("*.md"))
    assert len(files) == 1 and files[0].parent == log_dir and ".." not in files[0].name


def test_save_learning_log_rejects_empty(log_dir):
    assert "保存しませんでした" in tools.save_learning_log(" ", "本文")
    assert not log_dir.exists()


def test_tool_waits_for_approval_without_writing(log_dir):
    with agent.override(model=TestModel(call_tools=["save_learning_log"])):
        result = agent.run_sync("今日学んだことを記録して")
    assert isinstance(result.output, DeferredToolRequests)
    assert [c.tool_name for c in result.output.approvals] == ["save_learning_log"]
    assert not log_dir.exists()


def test_denied_call_does_not_write(log_dir):
    result = run_with_approval(agent, "今日学んだことを記録して",
                               TestModel(call_tools=["save_learning_log"]), answer=lambda _: "n")
    assert isinstance(result.output, str)
    assert not log_dir.exists()


def test_approved_call_writes(log_dir):
    result = run_with_approval(agent, "今日学んだことを記録して",
                               TestModel(call_tools=["save_learning_log"]), answer=lambda _: "y")
    assert isinstance(result.output, str)
    assert len(list(log_dir.glob("*.md"))) == 1
