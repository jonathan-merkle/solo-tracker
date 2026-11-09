import streamlit as st
from supabase import create_client

# Page configuration
st.set_page_config(page_title="Solo Tracker", page_icon="🎲")

# Connect to Supabase
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Title
st.title("🎲 Solo Tracker")

# Add New Game
with st.expander("Add Game"):

    with st.form("new_game"):

        game_name = st.text_input("Game Name")
        spreadsheet_url = st.text_input("Google Spreadsheet URL")
        bgg_url = st.text_input("BoardGameGeek URL")
        notes = st.text_area("Notes")

        save = st.form_submit_button("Save Game")

        if save and game_name:

            supabase.table("games").insert({
                "game_name": game_name,
                "spreadsheet_url": spreadsheet_url,
                "bgg_url": bgg_url,
                "notes": notes
            }).execute()

            st.success("Game added successfully")
            st.rerun()

# Load Games
response = (
    supabase
    .table("games")
    .select("*")
    .order("game_name")
    .execute()
)

games = response.data

# Collection Section
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

                    st.subheader(game["game_name"])

                    if game.get("notes"):
                        preview = game["notes"][:100]
                        if len(game["notes"]) > 100:
                            preview += "..."
                        st.caption(preview)

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

                    # Record Play Section
                    with st.expander("➕ Record Play"):

                        with st.form(f"play_form_{game['id']}"):

                            play_date = st.date_input(
                                "Play Date",
                                key=f"play_date_{game['id']}"
                            )

                            result = st.selectbox(
                                "Result",
                                ["Win", "Loss"],
                                key=f"result_{game['id']}"
                            )

                            score = st.number_input(
                                "Score",
                                value=0,
                                step=1,
                                key=f"score_{game['id']}"
                            )

                            play_notes = st.text_area(
                                "Notes",
                                key=f"notes_{game['id']}"
                            )

                            save_play = st.form_submit_button(
                                "Save Play"
                            )

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
