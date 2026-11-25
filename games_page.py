from datetime import date

import streamlit as st

from common import supabase, load_games, load_plays, record_play_dialog

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
        avg_play_time = st.number_input(
            "Average Play Time (minutes)",
            min_value=0,
            value=0,
            step=5
        )
        notes = st.text_area("Notes")

        save = st.form_submit_button("Save Game")

        if save and game_name:

            supabase.table("games").insert({
                "game_name": game_name,
                "spreadsheet_url": spreadsheet_url,
                "bgg_url": bgg_url,
                "image_url": image_url,
                "average_play_time_min": int(avg_play_time),
                "notes": notes
            }).execute()

            st.success("Game added successfully")
            st.rerun()

# --------------------------------------------------
# Load Data
# --------------------------------------------------

games = load_games()
games_dict = {str(game["id"]): game for game in games}
plays = load_plays()

# --------------------------------------------------
# Check URL for Auto-Opening Dialog
# --------------------------------------------------

# e.g., ?record_play=123
requested_game_id = st.query_params.get("record_play")

if requested_game_id and requested_game_id in games_dict:
    record_play_dialog(games_dict[requested_game_id])

# --------------------------------------------------
# Build Statistics
# --------------------------------------------------

play_counts = {}
last_played = {}
first_played = {}

for play in plays:

    game_id = str(play["game_id"])

    play_counts[game_id] = play_counts.get(game_id, 0) + 1

    play_date = play.get("play_date")

    if play_date:
        if game_id not in last_played or play_date > last_played[game_id]:
            last_played[game_id] = play_date
        if game_id not in first_played or play_date < first_played[game_id]:
            first_played[game_id] = play_date

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

                    st.subheader(game["game_name"])

                    metric_col1, metric_col2, metric_col3 = st.columns(3)

                    with metric_col1:
                        st.metric(
                            "Plays",
                            play_counts.get(str(game["id"]), 0)
                        )

                    with metric_col2:
                        total_min = (
                            play_counts.get(str(game["id"]), 0)
                            * (game.get("average_play_time_min") or 0)
                        )
                        hours, minutes = divmod(int(total_min), 60)
                        st.metric(
                            "Total Time",
                            f"{hours}h {minutes}m" if hours else f"{minutes}m"
                        )

                    with metric_col3:
                        last = last_played.get(str(game["id"]))
                        if last:
                            days = (date.today() - date.fromisoformat(last[:10])).days
                            if days <= 0:
                                label = "Today"
                            elif days < 14:
                                label = f"{days}d ago"
                            elif days < 60:
                                label = f"{days // 7}w ago"
                            elif days < 365:
                                label = f"{days // 30}mo ago"
                            else:
                                label = f"{days / 365.25:.1f}y ago"
                            icon = "🟢" if days <= 30 else "🟡" if days <= 180 else "🔴"
                            st.metric("Last Played", f"{icon} {label}", help=last[:10])
                        else:
                            st.metric("Last Played", "Never")

                    gid = str(game["id"])
                    if gid in first_played:
                        span_days = (
                            date.fromisoformat(last_played[gid][:10])
                            - date.fromisoformat(first_played[gid][:10])
                        ).days
                        years = span_days / 365.25
                        st.caption(
                            f"Playing for {years:.1f} years"
                            if years >= 1
                            else "Playing for less than a year"
                        )

                    if game.get("notes"):

                        preview = game["notes"][:100]

                        if len(game["notes"]) > 100:
                            preview += "..."

                        st.caption(preview)

                    btn_cols = st.columns(3)

                    with btn_cols[0]:
                        if game.get("spreadsheet_url"):
                            st.link_button(
                                "📊",
                                game["spreadsheet_url"],
                                help="Open spreadsheet",
                                use_container_width=True
                            )

                    with btn_cols[1]:
                        if game.get("bgg_url"):
                            st.markdown(
                                f'<a href="{game["bgg_url"]}" target="_blank" title="BoardGameGeek" '
                                'style="display:flex;align-items:center;justify-content:center;'
                                'height:38px;border:1px solid rgba(128,128,128,0.4);border-radius:8px;">'
                                '<img src="https://boardgamegeek.com/favicon.ico" width="20" height="20"></a>',
                                unsafe_allow_html=True
                            )

                    with btn_cols[2]:
                        if st.button(
                            "➕",
                            key=f"record_play_{game['id']}",
                            help="Record play",
                            use_container_width=True
                        ):
                            record_play_dialog(game)
