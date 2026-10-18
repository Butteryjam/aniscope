from collections import Counter


def build_genre_profile(anime_list):
    """Count how often each genre appears in the watchlist."""

    genre_profile = Counter()

    for anime in anime_list:
        genres = anime.get("genres", [])

        for genre in genres:
            genre_profile[genre] += 1

    return genre_profile


def get_recommendations(user_anime, candidates, top_n=8):
    """Return candidate anime ranked by genre similarity."""

    if not user_anime:
        return []

    genre_profile = build_genre_profile(user_anime)

    if not genre_profile:
        return []

    saved_ids = {anime["id"] for anime in user_anime}
    total_genre_weight = sum(genre_profile.values())

    scored_recommendations = []

    for candidate in candidates:
        if candidate["id"] in saved_ids:
            continue

        candidate_genres = candidate.get("genres", [])

        shared_genres = [
            genre
            for genre in candidate_genres
            if genre in genre_profile
        ]

        if not shared_genres:
            continue

        genre_score = sum(
            genre_profile[genre]
            for genre in shared_genres
        ) / total_genre_weight

        community_score = (candidate.get("averageScore") or 0) / 100

        final_score = (genre_score * 0.7) + (community_score * 0.3)

        explanation = (
            "Matches your watchlist genres: "
            + ", ".join(shared_genres[:3])
        )

        scored_recommendations.append(
            {
                "anime": candidate,
                "score": final_score,
                "explanation": explanation,
            }
        )

    scored_recommendations.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_recommendations[:top_n]