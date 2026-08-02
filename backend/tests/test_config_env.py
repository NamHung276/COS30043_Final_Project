import importlib
from pathlib import Path


def test_vite_prefixed_api_keys_are_used_as_fallback(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(repo_root)
    monkeypatch.delenv("RAWG_API_KEY", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    monkeypatch.setenv("VITE_RAWG_API_KEY", "rawg-test-key")
    monkeypatch.setenv("VITE_NEWS_API_KEY", "news-test-key")

    import backend.config as config

    importlib.reload(config)

    assert config.settings.rawg_api_key == "rawg-test-key"
    assert config.settings.news_api_key == "news-test-key"
