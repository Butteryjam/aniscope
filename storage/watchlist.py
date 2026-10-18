import json
from pathlib import Path

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"
WATCHLIST_FILE = DATA_FOLDER / "watchlist.json"

VALID_STATUSES = [
    "Plan to Watch",
    "Watching",
    "Completed",
    "Dropped",
]


def load_watchlist():
    """Return the saved watchlist as a Python list."""

    DATA_FOLDER.mkdir(exist_ok=True)

    if not WATCHLIST_FILE.exists():
        return []

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as file:
            saved_anime = json.load(file)

        if isinstance(saved_anime, list):
            return saved_anime

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_watchlist(watchlist):
    """Save the watchlist list into data/watchlist.json."""

    DATA_FOLDER.mkdir(exist_ok=True)

    with open(WATCHLIST_FILE, "w", encoding="utf-8") as file:
        json.dump(watchlist, file, indent=2, ensure_ascii=False)


def get_watchlist_ids():
    """Return the IDs of all saved anime."""

    return {anime["id"] for anime in load_watchlist()}


def get_watchlist_items():
    """Return every saved anime."""

    return load_watchlist()


def add_to_watchlist(anime, status="Plan to Watch"):
    """Save one anime unless it is already saved."""

    if status not in VALID_STATUSES:
        status = "Plan to Watch"

    watchlist = load_watchlist()

    if anime["id"] in get_watchlist_ids():
        return False

    title = anime["title"]["english"] or anime["title"]["romaji"]

    watchlist_item = {
        "id": anime["id"],
        "title": title,
        "cover_image": anime["coverImage"]["large"],
        "score": anime["averageScore"],
        "genres": anime["genres"],
        "status": status,
    }

    watchlist.append(watchlist_item)
    save_watchlist(watchlist)

    return True


def remove_from_watchlist(anime_id):
    """Remove an anime using its AniList ID."""

    watchlist = load_watchlist()

    updated_watchlist = [
        anime for anime in watchlist
        if anime["id"] != anime_id
    ]

    if len(updated_watchlist) == len(watchlist):
        return False

    save_watchlist(updated_watchlist)
    return True


def update_watchlist_status(anime_id, new_status):
    """Update the status of one saved anime."""

    if new_status not in VALID_STATUSES:
        return False

    watchlist = load_watchlist()

    for anime in watchlist:
        if anime["id"] == anime_id:
            anime["status"] = new_status
            save_watchlist(watchlist)
            return True

    return False