import streamlit as st
import pandas as pd
from supabase import create_client

# Connect to Supabase
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.set_page_config(page_title="Solo Tracker", page_icon="🎲")

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

st.header("My Collection")

if not games:
    st.info("No games found.")
else:

    for game in games:

        st.subheader(game["game_name"])

        cols = st.columns(2)

        if game.get("spreadsheet_url"):
            with cols[0]:
                st.link_button(
                    "📊 Spreadsheet",
                    game["spreadsheet_url"]
                )

        if game.get("bgg_url"):
            with cols[1]:
                st.link_button(
                    "🎲 BoardGameGeek",
                    game["bgg_url"]
                )

        if game.get("notes"):
            st.write(game["notes"])

        st.divider()
