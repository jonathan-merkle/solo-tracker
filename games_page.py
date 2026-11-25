import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


supabase = get_supabase()


def load_games():
    response = (
        supabase
        .table("games")
        .select("*")
        .order("game_name")
        .execute()
    )
    return response.data or []


def load_plays():
    plays = []
    page_size = 1000
    offset = 0

    # Supabase caps each request (default 1000 rows), so page through all plays
    while True:
        batch = (
            supabase
            .table("plays")
            .select("game_id, play_date, result")
            .order("id")
            .range(offset, offset + page_size - 1)
            .execute()
            .data
        ) or []
        plays.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size

    return plays


@st.dialog("Record Play")
def record_play_dialog(game):

    with st.form(f"play_form_{game['id']}"):

        st.subheader(game["game_name"])

        play_date = st.date_input("Play Date")

        result = st.selectbox(
            "Result",
            ["Win", "Loss", "Finished"]
        )

        # Text input because mobile number keypads often lack a minus sign
        score_text = st.text_input(
            "Score",
            value="0"
        )

        play_notes = st.text_area("Notes")

        save_play = st.form_submit_button("Save Play")

        if save_play:

            try:
                score = int(score_text.strip().replace("−", "-"))
            except ValueError:
                st.error("Score must be a whole number, e.g. -5 or 42.")
                st.stop()

            supabase.table("plays").insert({
                "game_id": game["id"],
                "play_date": str(play_date),
                "result": result,
                "score": score,
                "notes": play_notes
            }).execute()

            st.success("Play recorded!")
            st.rerun()
