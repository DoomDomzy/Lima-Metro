import json

from data_osm import _cache_meta_path, _cache_key, cache_is_fresh, save_cache_meta


def test_cache_is_fresh_after_save():
    save_cache_meta()
    assert cache_is_fresh()


def test_cache_is_stale_when_key_changes(tmp_path, monkeypatch):
    save_cache_meta()
    assert cache_is_fresh()
    _cache_meta_path().write_text(json.dumps({"cache_key": "stale-key"}))
    assert not cache_is_fresh()


def test_cache_is_stale_when_meta_missing(tmp_path, monkeypatch):
    if _cache_meta_path().exists():
        _cache_meta_path().unlink()
    assert not cache_is_fresh()
