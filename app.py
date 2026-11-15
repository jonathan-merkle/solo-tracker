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

# Create a lookup dictionary for convenience
games_dict = {str(game["id"]): game for game in games}

# --------------------------------------------------
# Check URL for Auto-Opening Dialog
# --------------------------------------------------

# Check if 'record_play' exists in the URL query parameters (e.g., ?record_play=123)
requested_game_id = st.query_params.get("record_play")

if requested_game_id and requested_game_id in games_dict:
    # Automatically trigger the dialog for this game on load
    record_play_dialog(games_dict[requested_game_id])

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
