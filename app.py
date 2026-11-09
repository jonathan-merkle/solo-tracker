import streamlit as st
from supabase import create_client

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Solo Tracker",
    page_icon="🎲",
    layout="wide"
)

# --------------------------------------------------
# Supabase Connection
# --------------------------------------------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# --------------------------------------------------
# Record Play Dialog
# --------------------------------------------------

@st.dialog("Record Play")
def record_play_dialog(game):

    with st.form(f"play_form_{game['id']}"):

        st.subheader(game["game_name"])

        play_date = st.date_input("Play Date")

        result = st.selectbox(
            "Result",
            ["Win", "Loss"]
        )

        score = st.number_input(
            "Score",
            value=0,
            step=1
        )

        play_notes = st.text_area("Notes")

        save_play = st.form_submit_button("Save Play")

        if save_play:

            supabase.table("plays").insert({
                "game_id": game["id"],
                "play_date": str(play_date),
                "result": result,
                "score": int(score),
                "notes": play_notes
            }).execute()

            st.success("Play recorded!")
            st.rerun()

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🎲 Solo Tracker")

# --------------------------------------------------
# Add New Game
# --------------------------------------------------

with st.expander("Add Game"):

    with st.form("new_game"):

        game_name = st.text_input("Game Name")
        spreadsheet_url = st.text_input("Google Spreadsheet URL")
        bgg_url = st.text_input("BoardGameGeek URL")
        image_url = st.text_input("Image URL")
        notes = st.text_area("Notes")

        save = st.form_submit_button("Save Game")

        if save and game_name:

            supabase.table("games").insert({
                "game_name": game_name,
                "spreadsheet_url": spreadsheet_url,
                "bgg_url": bgg_url,
                "image_url": image_url,
                "notes": notes
            }).execute()

            st.success("Game added successfully")
            st.rerun()

# --------------------------------------------------
# Load Games
# --------------------------------------------------

games_response = (
    supabase
    .table("games")
    .select("*")
    .order("game_name")
    .execute()
)

games = games_response.data or []

# --------------------------------------------------
# Load Plays
# --------------------------------------------------

plays_response = (
    supabase
    .table("plays")
    .select("*")
    .execute()
)

plays = plays_response.data or []

# --------------------------------------------------
# Build Statistics
# --------------------------------------------------

play_counts = {}
last_played = {}

for play in plays:

    game_id = play["game_id"]

    play_counts[game_id] = (
        play_counts.get(game_id, 0) + 1
    )

    play_date = play.get("play_date")

    if play_date:

        if (
            game_id not in last_played or
            play_date > last_played[game_id]
        ):
            last_played[game_id] = play_date

# --------------------------------------------------
# Collection
# --------------------------------------------------

st.header("My Collection")

if not games:

    st.info("No games found.")

else:

    cols_per_row = 3

    for i in range(0, len(games), cols_per_row):

        row_cols = st.columns(cols_per_row)

        for col, game in zip(row_cols, games[i:i + cols_per_row]):

            with col:

                with st.container(border=True):

                    # ------------------------------
                    # Cover Image
                    # ------------------------------

                    try:
                        if game.get("image_url"):
                            st.image(
                                game["image_url"],
                                use_container_width=True
                            )
                    except Exception:
                        pass

                    # ------------------------------
                    # Game Name
                    # ------------------------------

                    st.subheader(game["game_name"])

                    # ------------------------------
                    # Statistics
                    # ------------------------------

                    metric_col1, metric_col2 = st.columns(2)

                    with metric_col1:
                        st.metric(
                            "Plays",
                            play_counts.get(
                                game["id"],
                                0
                            )
                        )

                    with metric_col2:
                        st.metric(
                            "Last Played",
                            last_played.get(
                                game["id"],
                                "Never"
                            )
                        )

                    # ------------------------------
                    # Notes
                    # ------------------------------

                    if game.get("notes"):

                        preview = game["notes"][:100]

                        if len(game["notes"]) > 100:
                            preview += "..."

                        st.caption(preview)

                    # ------------------------------
                    # Links
                    # ------------------------------

                    if game.get("spreadsheet_url"):

                        st.link_button(
                            "📊 Spreadsheet",
                            game["spreadsheet_url"],
                            use_container_width=True
                        )

                    if game.get("bgg_url"):

                        st.link_button(
                            "🎲 BoardGameGeek",
                            game["bgg_url"],
                            use_container_width=True
                        )

                    # ------------------------------
                    # Record Play Button
                    # ------------------------------

                    if st.button(
                        "➕ Record Play",
                        key=f"record_play_{game['id']}",
                        use_container_width=True
                    ):
                        record_play_dialog(game)
