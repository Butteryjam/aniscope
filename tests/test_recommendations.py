from services.recommendations import (
    build_genre_profile,
    get_recommendations,
)


def test_build_genre_profile_counts_genres():
    anime_list = [
        {"genres": ["Action", "Fantasy"]},
        {"genres": ["Action", "Drama"]},
    ]

    profile = build_genre_profile(anime_list)

    assert profile["Action"] == 2
    assert profile["Fantasy"] == 1
    assert profile["Drama"] == 1


def test_recommendations_exclude_saved_anime():
    user_anime = [
        {
            "id": 1,
            "genres": ["Action", "Fantasy"],
        }
    ]

    candidates = [
        {
            "id": 1,
            "genres": ["Action", "Fantasy"],
            "averageScore": 90,
        },
        {
            "id": 2,
            "genres": ["Action", "Adventure"],
            "averageScore": 85,
        },
        {
            "id": 3,
            "genres": ["Romance"],
            "averageScore": 95,
        },
    ]

    recommendations = get_recommendations(
        user_anime,
        candidates,
    )

    assert len(recommendations) == 1
    assert recommendations[0]["anime"]["id"] == 2
    assert "Action" in recommendations[0]["explanation"]