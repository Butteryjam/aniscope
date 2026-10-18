from storage import watchlist


def sample_anime():
    return {
        "id": 100,
        "title": {
            "english": "Test Anime",
            "romaji": "Test Anime",
        },
        "coverImage": {
            "large": "https://example.com/image.jpg",
        },
        "averageScore": 80,
        "genres": ["Action", "Fantasy"],
    }


def use_temporary_watchlist(monkeypatch, tmp_path):
    """Make the test use a temporary JSON file, not your real watchlist."""

    data_folder = tmp_path / "data"
    watchlist_file = data_folder / "watchlist.json"

    monkeypatch.setattr(watchlist, "DATA_FOLDER", data_folder)
    monkeypatch.setattr(watchlist, "WATCHLIST_FILE", watchlist_file)


def test_add_anime_to_watchlist(monkeypatch, tmp_path):
    use_temporary_watchlist(monkeypatch, tmp_path)

    added = watchlist.add_to_watchlist(sample_anime())
    saved_anime = watchlist.get_watchlist_items()

    assert added is True
    assert len(saved_anime) == 1
    assert saved_anime[0]["title"] == "Test Anime"


def test_cannot_add_same_anime_twice(monkeypatch, tmp_path):
    use_temporary_watchlist(monkeypatch, tmp_path)

    watchlist.add_to_watchlist(sample_anime())
    added_again = watchlist.add_to_watchlist(sample_anime())

    assert added_again is False
    assert len(watchlist.get_watchlist_items()) == 1


def test_update_and_remove_anime(monkeypatch, tmp_path):
    use_temporary_watchlist(monkeypatch, tmp_path)

    watchlist.add_to_watchlist(sample_anime())

    status_changed = watchlist.update_watchlist_status(
        100,
        "Completed",
    )

    assert status_changed is True
    assert watchlist.get_watchlist_items()[0]["status"] == "Completed"

    removed = watchlist.remove_from_watchlist(100)

    assert removed is True
    assert watchlist.get_watchlist_items() == []