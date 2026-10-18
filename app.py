import html

import plotly.express as px
import streamlit as st

from api.anilist import (
    get_anime_details,
    get_trending_anime,
    get_trending_anime_page,
    search_anime_page,
)
from services.analytics import (
    format_distribution,
    genre_distribution,
    score_distribution,
)
from services.recommendations import get_recommendations
from storage.watchlist import (
    VALID_STATUSES,
    add_to_watchlist,
    get_watchlist_ids,
    get_watchlist_items,
    remove_from_watchlist,
    update_watchlist_status,
)

st.set_page_config(
    page_title="AniScope",
    page_icon="🌌",
    layout="wide",
)

st.markdown(
    """
    <style>
    .anime-cover {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 10px;
        display: block;
    }

    .anime-card-title {
        min-height: 92px;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 8px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #3b315f;
        border-radius: 14px;
        background-color: #141c2e;
        padding: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "selected_anime_id" not in st.session_state:
    st.session_state.selected_anime_id = None

if "discover_page" not in st.session_state:
    st.session_state.discover_page = 1

if "last_discover_request" not in st.session_state:
    st.session_state.last_discover_request = ""


@st.cache_data(ttl=300)
def cached_trending_anime():
    return get_trending_anime()


@st.cache_data(ttl=300)
def cached_trending_anime_page(
    page,
    genre,
    format_type,
    year,
    status,
):
    return get_trending_anime_page(
        page=page,
        per_page=24,
        genre=genre,
        format_type=format_type,
        year=year,
        status=status,
    )


@st.cache_data(ttl=300)
def cached_search_anime_page(
    search_term,
    page,
    genre,
    format_type,
    year,
    status,
):
    return search_anime_page(
        search_term,
        page=page,
        per_page=24,
        genre=genre,
        format_type=format_type,
        year=year,
        status=status,
    )


@st.cache_data(ttl=300)
def cached_anime_details(anime_id):
    return get_anime_details(anime_id)


def open_anime_details(anime_id):
    st.session_state.selected_anime_id = anime_id
    st.rerun()


def show_anime_cards(anime_list):
    if not anime_list:
        st.info("No anime found.")
        return

    saved_anime_ids = get_watchlist_ids()

    for row_start in range(0, len(anime_list), 4):
        row_anime = anime_list[row_start:row_start + 4]
        columns = st.columns(4)

        for column, anime in zip(columns, row_anime):
            with column:
                with st.container(border=True):
                    title = (
                        anime["title"]["english"]
                        or anime["title"]["romaji"]
                    )
                    image_url = anime["coverImage"]["large"]
                    score = anime["averageScore"] or "No score yet"
                    genres = ", ".join(anime["genres"][:3])

                    safe_title = html.escape(title)
                    safe_image_url = html.escape(
                        image_url,
                        quote=True,
                    )

                    st.markdown(
                        f'<img class="anime-cover" src="{safe_image_url}">',
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f'<div class="anime-card-title">{safe_title}</div>',
                        unsafe_allow_html=True,
                    )

                    st.write(f"Score: {score}")
                    st.caption(genres)

                    if st.button(
                        "View details",
                        key=f"details_{anime['id']}",
                    ):
                        open_anime_details(anime["id"])

                    if anime["id"] in saved_anime_ids:
                        st.success("✓ In your watchlist")

                    elif st.button(
                        "➕ Add to watchlist",
                        key=f"add_{anime['id']}",
                    ):
                        add_to_watchlist(anime)
                        st.rerun()


def render_pagination(page_info):
    left_column, middle_column, right_column = st.columns([1, 2, 1])

    with left_column:
        if st.button(
            "← Previous",
            disabled=st.session_state.discover_page == 1,
        ):
            st.session_state.discover_page -= 1
            st.rerun()

    with middle_column:
        st.markdown(
            f"<p style='text-align: center;'>"
            f"Page {page_info['currentPage']}"
            f"</p>",
            unsafe_allow_html=True,
        )

    with right_column:
        if st.button(
            "Next →",
            disabled=not page_info["hasNextPage"],
        ):
            st.session_state.discover_page += 1
            st.rerun()


def render_discover_page():
    st.title("🌌 AniScope")
    st.write("Discover and search for anime.")

    search_term = st.text_input(
        "Search for an anime",
        placeholder="For example: Naruto, One Piece, Death Note",
    )

    genre_column, format_column, year_column, status_column = st.columns(4)

    with genre_column:
        selected_genre = st.selectbox(
            "Genre",
            [
                "All",
                "Action",
                "Adventure",
                "Comedy",
                "Drama",
                "Fantasy",
                "Horror",
                "Mystery",
                "Romance",
                "Sci-Fi",
                "Slice of Life",
                "Sports",
            ],
        )

    with format_column:
        selected_format = st.selectbox(
            "Format",
            ["All", "TV", "MOVIE", "OVA", "ONA", "SPECIAL"],
        )

    with year_column:
        selected_year = st.selectbox(
            "Release year",
            ["All"] + list(range(2026, 1960, -1)),
        )

    with status_column:
        selected_status = st.selectbox(
            "Airing status",
            [
                "All",
                "Currently Releasing",
                "Finished",
                "Not Yet Released",
            ],
        )

    genre = None if selected_genre == "All" else selected_genre
    format_type = None if selected_format == "All" else selected_format
    year = None if selected_year == "All" else selected_year

    status_map = {
        "All": None,
        "Currently Releasing": "RELEASING",
        "Finished": "FINISHED",
        "Not Yet Released": "NOT_YET_RELEASED",
    }

    status = status_map[selected_status]

    request_name = (
        f"{search_term}|{genre}|{format_type}|{year}|{status}"
    )

    if request_name != st.session_state.last_discover_request:
        st.session_state.discover_page = 1
        st.session_state.last_discover_request = request_name

    current_page = st.session_state.discover_page

    try:
        if search_term.strip():
            st.subheader(f"Search results for: {search_term}")

            with st.spinner("Searching AniList..."):
                result = cached_search_anime_page(
                    search_term,
                    current_page,
                    genre,
                    format_type,
                    year,
                    status,
                )

        else:
            st.subheader("Trending Anime")

            with st.spinner("Getting anime from AniList..."):
                result = cached_trending_anime_page(
                    current_page,
                    genre,
                    format_type,
                    year,
                    status,
                )

        show_anime_cards(result["media"])
        render_pagination(result["pageInfo"])

    except RuntimeError as error:
        st.error(str(error))


def render_watchlist_page():
    st.title("📋 My Watchlist")

    watchlist = get_watchlist_items()

    if not watchlist:
        st.info("Your watchlist is empty. Add anime from the Discover page.")
        return

    selected_status = st.selectbox(
        "Filter by status",
        ["All"] + VALID_STATUSES,
    )

    if selected_status != "All":
        watchlist = [
            anime
            for anime in watchlist
            if anime.get("status", "Plan to Watch") == selected_status
        ]

    if not watchlist:
        st.info("No anime match this status.")
        return

    columns = st.columns(4)

    for index, anime in enumerate(watchlist):
        with columns[index % 4]:
            st.image(anime["cover_image"])
            st.subheader(anime["title"])
            st.write(f"Score: {anime['score'] or 'No score yet'}")
            st.caption(", ".join(anime["genres"][:3]))

            if st.button(
                "View details",
                key=f"watchlist_details_{anime['id']}",
            ):
                open_anime_details(anime["id"])

            current_status = anime.get("status", "Plan to Watch")

            if current_status not in VALID_STATUSES:
                current_status = "Plan to Watch"

            new_status = st.selectbox(
                "Status",
                VALID_STATUSES,
                index=VALID_STATUSES.index(current_status),
                key=f"status_{anime['id']}",
            )

            if new_status != current_status:
                update_watchlist_status(anime["id"], new_status)
                st.rerun()

            if st.button("🗑️ Remove", key=f"remove_{anime['id']}"):
                remove_from_watchlist(anime["id"])
                st.rerun()


def render_recommendations_page():
    st.title("💡 Smart Recommendations")
    st.write("Suggestions based on the genres in your watchlist.")

    watchlist = get_watchlist_items()

    if not watchlist:
        st.info("Add anime to your watchlist before requesting recommendations.")
        return

    try:
        with st.spinner("Finding recommendations..."):
            trending_anime = cached_trending_anime()

        recommendations = get_recommendations(
            watchlist,
            trending_anime,
        )

    except RuntimeError as error:
        st.error(str(error))
        return

    if not recommendations:
        st.info("No matching recommendations were found yet.")
        return

    columns = st.columns(4)
    saved_anime_ids = get_watchlist_ids()

    for index, recommendation in enumerate(recommendations):
        anime = recommendation["anime"]

        with columns[index % 4]:
            title = anime["title"]["english"] or anime["title"]["romaji"]
            image_url = anime["coverImage"]["large"]
            score = anime["averageScore"] or "No score yet"

            st.image(image_url)
            st.subheader(title)
            st.write(f"Score: {score}")
            st.caption(recommendation["explanation"])

            if st.button(
                "View details",
                key=f"recommendation_details_{anime['id']}",
            ):
                open_anime_details(anime["id"])

            if anime["id"] in saved_anime_ids:
                st.success("✓ In your watchlist")

            elif st.button(
                "➕ Add to watchlist",
                key=f"recommendation_{anime['id']}",
            ):
                add_to_watchlist(anime)
                st.rerun()


def render_analytics_page():
    st.title("📊 Anime Analytics")

    data_source = st.radio(
        "Choose data to analyse",
        ["Trending anime", "My Watchlist"],
    )

    try:
        if data_source == "Trending anime":
            with st.spinner("Getting anime data..."):
                anime_list = cached_trending_anime()
        else:
            anime_list = get_watchlist_items()

    except RuntimeError as error:
        st.error(str(error))
        return

    if not anime_list:
        st.info("There is no anime data to analyse yet.")
        return

    st.caption(f"Analysing {len(anime_list)} anime")

    genres = genre_distribution(anime_list)
    scores = score_distribution(anime_list)
    formats = format_distribution(anime_list)

    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Most common genres")

        if not genres.empty:
            genre_chart = px.bar(
                genres.head(10),
                x="Genre",
                y="Count",
                color="Count",
            )
            st.plotly_chart(genre_chart, width="stretch")

    with right_column:
        st.subheader("Anime formats")

        if not formats.empty:
            format_chart = px.pie(
                formats,
                names="Format",
                values="Count",
                hole=0.4,
            )
            st.plotly_chart(format_chart, width="stretch")

    st.subheader("Community-score distribution")

    if not scores.empty:
        score_chart = px.histogram(
            scores,
            x="Score",
            nbins=10,
        )
        st.plotly_chart(score_chart, width="stretch")


def render_detail_page(anime_id):
    if st.button("← Back to the app"):
        st.session_state.selected_anime_id = None
        st.rerun()

    try:
        with st.spinner("Getting anime details..."):
            anime = cached_anime_details(anime_id)

    except RuntimeError as error:
        st.error(str(error))
        return

    title = anime["title"]["english"] or anime["title"]["romaji"]
    studios = anime.get("studios", {}).get("nodes", [])
    studio_names = ", ".join(studio["name"] for studio in studios)

    image_column, information_column = st.columns([1, 2])

    with image_column:
        st.image(anime["coverImage"]["large"])

    with information_column:
        st.title(title)
        st.write(f"Score: {anime['averageScore'] or 'No score yet'}")
        st.write(f"Format: {anime['format'] or 'Unknown'}")
        st.write(f"Episodes: {anime['episodes'] or 'Unknown'}")
        st.write(f"Release year: {anime['seasonYear'] or 'Unknown'}")
        st.write(f"Studio: {studio_names or 'Unknown'}")
        st.caption(", ".join(anime["genres"]))

        if anime["id"] in get_watchlist_ids():
            st.success("✓ In your watchlist")

        elif st.button("➕ Add to watchlist", key="detail_add"):
            add_to_watchlist(anime)
            st.rerun()

        if anime.get("siteUrl"):
            st.link_button("Open on AniList", anime["siteUrl"])

    st.subheader("Synopsis")
    st.write(anime["description"] or "No synopsis is available.")


with st.sidebar:
    st.title("🌌 AniScope")

    page = st.radio(
        "Navigate",
        ["Discover", "My Watchlist", "Recommendations", "Analytics"],
    )

    st.divider()
    st.caption(f"{len(get_watchlist_ids())} anime saved")


if st.session_state.selected_anime_id is not None:
    render_detail_page(st.session_state.selected_anime_id)

elif page == "Discover":
    render_discover_page()

elif page == "My Watchlist":
    render_watchlist_page()

elif page == "Recommendations":
    render_recommendations_page()

elif page == "Analytics":
    render_analytics_page()