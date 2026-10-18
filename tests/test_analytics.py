from services.analytics import genre_distribution


def test_genre_distribution_counts_anime_genres():
    anime_list = [
        {"genres": ["Action", "Fantasy"]},
        {"genres": ["Action", "Drama"]},
        {"genres": ["Action"]},
    ]

    result = genre_distribution(anime_list)

    genre_counts = dict(
        zip(result["Genre"], result["Count"])
    )

    assert genre_counts["Action"] == 3
    assert genre_counts["Fantasy"] == 1
    assert genre_counts["Drama"] == 1