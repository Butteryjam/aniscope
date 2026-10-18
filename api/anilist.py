import requests

ANILIST_API_URL = "https://graphql.anilist.co"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

MEDIA_FIELDS = """
id
title {
  romaji
  english
}
coverImage {
  large
}
averageScore
genres
format
seasonYear
"""

ANIME_DETAIL_QUERY = """
query ($id: Int!) {
  Media(id: $id, type: ANIME) {
    id
    title {
      romaji
      english
      native
    }
    coverImage {
      large
    }
    description(asHtml: false)
    episodes
    duration
    status
    format
    seasonYear
    averageScore
    genres
    siteUrl
    studios(isMain: true) {
      nodes {
        name
      }
    }
  }
}
"""


def execute_graphql(query, variables=None):
    """Send one GraphQL request to AniList."""

    clean_variables = {
        key: value
        for key, value in (variables or {}).items()
        if value is not None
    }

    try:
        response = requests.post(
            ANILIST_API_URL,
            json={
                "query": query,
                "variables": clean_variables,
            },
            headers=HEADERS,
            timeout=15,
        )
        response_data = response.json()

    except requests.RequestException as error:
        raise RuntimeError(f"Network problem: {error}") from error

    except ValueError as error:
        raise RuntimeError("AniList did not return valid JSON data.") from error

    if response_data.get("errors"):
        messages = [
            error.get("message", "Unknown AniList error")
            for error in response_data["errors"]
        ]
        raise RuntimeError("AniList says: " + " | ".join(messages))

    if not response.ok:
        raise RuntimeError(
            f"AniList request failed with status {response.status_code}."
        )

    return response_data["data"]


def get_media_page(
    page,
    per_page,
    sort,
    search_term=None,
    genre=None,
    format_type=None,
    status=None,
):
    """Build a query containing only filters the user selected."""

    variable_definitions = [
        "$page: Int!",
        "$perPage: Int!",
    ]

    variables = {
        "page": page,
        "perPage": per_page,
    }

    media_arguments = [
        "type: ANIME",
        f"sort: [{sort}]",
    ]

    if search_term:
        variable_definitions.append("$search: String!")
        variables["search"] = search_term
        media_arguments.append("search: $search")

    if genre:
        variable_definitions.append("$genre: String!")
        variables["genre"] = genre
        media_arguments.append("genre: $genre")

    if format_type:
        variable_definitions.append("$format: MediaFormat!")
        variables["format"] = format_type
        media_arguments.append("format: $format")

    if status:
        variable_definitions.append("$status: MediaStatus!")
        variables["status"] = status
        media_arguments.append("status: $status")

    query = f"""
    query ({", ".join(variable_definitions)}) {{
      Page(page: $page, perPage: $perPage) {{
        pageInfo {{
          currentPage
          hasNextPage
        }}
        media({", ".join(media_arguments)}) {{
          {MEDIA_FIELDS}
        }}
      }}
    }}
    """

    data = execute_graphql(query, variables)
    return data["Page"]


def get_trending_anime_page(
    page=1,
    per_page=24,
    genre=None,
    format_type=None,
    year=None,
    status=None,
):
    return get_media_page(
        page=page,
        per_page=per_page,
        sort="TRENDING_DESC",
        genre=genre,
        format_type=format_type,
        status=status,
    )


def get_trending_anime():
    return get_trending_anime_page()["media"]


def search_anime_page(
    search_term,
    page=1,
    per_page=24,
    genre=None,
    format_type=None,
    year=None,
    status=None,
):
    clean_search_term = search_term.strip()

    if not clean_search_term:
        return {
            "media": [],
            "pageInfo": {
                "currentPage": 1,
                "hasNextPage": False,
            },
        }

    return get_media_page(
        page=page,
        per_page=per_page,
        sort="SEARCH_MATCH",
        search_term=clean_search_term,
        genre=genre,
        format_type=format_type,
        status=status,
    )


def get_anime_details(anime_id):
    data = execute_graphql(
        ANIME_DETAIL_QUERY,
        variables={"id": anime_id},
    )
    return data["Media"]