from collections import Counter

import pandas as pd


def genre_distribution(anime_list):
    """Return genre counts as a table."""

    genre_counter = Counter()

    for anime in anime_list:
        for genre in anime.get("genres", []):
            genre_counter[genre] += 1

    return pd.DataFrame(
        genre_counter.items(),
        columns=["Genre", "Count"],
    ).sort_values("Count", ascending=False)


def score_distribution(anime_list):
    """Return valid AniList scores as a table."""

    scores = [
        anime["averageScore"]
        for anime in anime_list
        if anime.get("averageScore")
    ]

    return pd.DataFrame({"Score": scores})


def format_distribution(anime_list):
    """Return anime-format counts as a table."""

    format_counter = Counter()

    for anime in anime_list:
        anime_format = anime.get("format", "Unknown")
        format_counter[anime_format] += 1

    return pd.DataFrame(
        format_counter.items(),
        columns=["Format", "Count"],
    ).sort_values("Count", ascending=False)