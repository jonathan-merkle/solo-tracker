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
# Search
# --------------------------------------------------

search_query = st.text_input("🔍 Search games", placeholder="Type a game name and press Enter...", key="game_search")
search_query = search_query.strip().lower()

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

plays = []
page_size = 1000
offset = 0

# Supabase caps each request (default 1000 rows), so page through all plays
while True:
    batch = (
        supabase
        .table("plays")
        .select("game_id, play_date")
        .order("id")
        .range(offset, offset + page_size - 1)
        .execute()
        .data
    ) or []
    plays.extend(batch)
    if len(batch) < page_size:
        break
    offset += page_size

# --------------------------------------------------
# Build Statistics
# --------------------------------------------------

play_counts = {}
last_played = {}

for play in plays:

    game_id = str(play["game_id"])

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
# Plays Per Month (last 12 months)
# --------------------------------------------------

import pandas as pd
from datetime import date

today = date.today()
months = []
y, m = today.year, today.month
for _ in range(12):
    months.append(f"{y}-{m:02d}")
    m -= 1
    if m == 0:
        y, m = y - 1, 12
months.reverse()

monthly_counts = {key: 0 for key in months}
for play in plays:
    key = (play.get("play_date") or "")[:7]
    if key in monthly_counts:
        monthly_counts[key] += 1

st.header("Plays Per Month")
st.bar_chart(
    pd.DataFrame({"Plays": list(monthly_counts.values())}, index=months)
)

# --------------------------------------------------
# Collection
# --------------------------------------------------

st.header("My Collection")

if search_query:
    games = [g for g in games if search_query in g["game_name"].lower()]

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
                        
                            img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        
                            with img_col2:
                                st.image(
                                    game["image_url"],
                                    width=160
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
                                str(game["id"]),
                                0
                            )
                        )

                    with metric_col2:
                        st.metric(
                            "Last Played",
                            last_played.get(
                                str(game["id"]),
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

                        btn_col, copy_col = st.columns([5, 1])

                        with btn_col:
                            st.link_button(
                                "📊 Spreadsheet",
                                game["spreadsheet_url"],
                                use_container_width=True
                            )

                        with copy_col:
                            direct_url = f"https://solo-tracker.streamlit.app/?record_play={game['id']}"
                            
                            st.components.v1.html(f"""
                                <div style="display: flex; align-items: center; justify-content: center; margin: 0; padding: 0;">
                                    <button onclick="navigator.clipboard.writeText('{direct_url}'); this.innerText='✅';" title="Copy Direct Record Play Link" style="
                                        width: 100%;
                                        height: 38px;
                                        background-color: rgb(255, 255, 255);
                                        border: 1px solid rgba(49, 51, 63, 0.2);
                                        border-radius: 4px;
                                        cursor: pointer;
                                        font-size: 1rem;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        transition: background-color 0.2s;
                                    ">📋</button>
                                </div>
                            """, height=38)

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
