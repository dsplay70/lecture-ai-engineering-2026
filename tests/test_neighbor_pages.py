"""第5回 宿題（実装）: 検索結果に前後ページを付ける処理のテスト（APIキー不要）。"""

from app.retrieval import add_neighbor_pages, load_pages


def _hit(page_id: str) -> dict:
    page = next(p for p in load_pages() if p["page_id"] == page_id)
    return {**page, "distance": 0.1}


def test_window_0_returns_hits_unchanged():
    hits = [_hit("lec02-main-p052")]
    assert add_neighbor_pages(hits, window=0) == hits


def test_adds_previous_and_next_page_in_order():
    results = add_neighbor_pages([_hit("lec02-main-p052")], window=1)
    assert [r["page_id"] for r in results] == ["lec02-main-p051", "lec02-main-p052", "lec02-main-p053"]
    assert [r["role"] for r in results] == ["neighbor", "hit", "neighbor"]
    assert results[0]["neighbor_of"] == "lec02-main-p052"
    assert "distance" not in results[0]


def test_no_duplicates_when_hits_are_adjacent():
    results = add_neighbor_pages([_hit("lec02-main-p052"), _hit("lec02-main-p051")], window=1)
    ids = [r["page_id"] for r in results]
    assert len(ids) == len(set(ids))
    assert set(ids) == {"lec02-main-p050", "lec02-main-p051", "lec02-main-p052", "lec02-main-p053"}


def test_does_not_cross_documents():
    first = next(p for p in load_pages() if p["document_id"] == "lec02-main")
    results = add_neighbor_pages([{**first, "distance": 0.1}], window=1)
    assert {r["document_id"] for r in results} == {"lec02-main"}
    assert [r["page"] for r in results] == [first["page"], first["page"] + 1]
