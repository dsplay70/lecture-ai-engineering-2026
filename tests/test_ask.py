from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(prompt_token_count=12, candidates_token_count=7),
        text="回答",
    )
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **kwargs: response)
    ))
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("質問") == "回答"
    assert capsys.readouterr().out.strip() == "[tokens] input=12 output=7"


def test_ask_handles_missing_usage_metadata(monkeypatch, capsys):
    response = SimpleNamespace(usage_metadata=None, text="回答")
    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **kwargs: response)
    ))
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    ask_module.ask("質問")
    assert capsys.readouterr().out.strip() == "[tokens] input=不明 output=不明"