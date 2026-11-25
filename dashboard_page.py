from datetime import date

import pandas as pd
import streamlit as st

from common import load_games, load_plays

st.title("📊 Dashboard")

games_dict = {str(game["id"]): game for game in load_games()}
plays = load_plays()

# --------------------------------------------------
# Plays Per Month (last 24 months)
# --------------------------------------------------

today = date.today()
months = []
y, m = today.year, today.month
for _ in range(24):
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
# Minutes Played by Month (last 24 months)
# --------------------------------------------------

minutes_by_month = {key: 0 for key in months}
for play in plays:
    key = (play.get("play_date") or "")[:7]
    game = games_dict.get(str(play["game_id"]))
    if key in minutes_by_month and game:
        minutes_by_month[key] += game.get("average_play_time_min") or 0

st.header("Minutes Played by Month (Last 24 Months)")
st.bar_chart(
    pd.DataFrame({"Minutes": list(minutes_by_month.values())}, index=months)
)

# --------------------------------------------------
# Plays by Game (last 3 months)
# --------------------------------------------------

cutoff_month = months[-3]
recent_counts = {}
for play in plays:
    if (play.get("play_date") or "")[:7] >= cutoff_month:
        game_id = str(play["game_id"])
        recent_counts[game_id] = recent_counts.get(game_id, 0) + 1

recent_rows = [
    {"Game": games_dict[gid]["game_name"], "Plays": count}
    for gid, count in sorted(recent_counts.items(), key=lambda item: item[1], reverse=True)
    if gid in games_dict
]

st.header("Plays by Game (Last 3 Months)")

if recent_rows:
    st.vega_lite_chart(
        pd.DataFrame(recent_rows),
        {
            "mark": {"type": "arc", "tooltip": True},
            "encoding": {
                "theta": {"field": "Plays", "type": "quantitative", "stack": True},
                "color": {"field": "Game", "type": "nominal", "sort": {"field": "Plays", "order": "descending"}},
                "tooltip": [
                    {"field": "Game", "type": "nominal"},
                    {"field": "Plays", "type": "quantitative"},
                ],
            },
        },
        use_container_width=True,
    )
else:
    st.info("No plays recorded in the last 3 months.")

# --------------------------------------------------
# Share of Plays (top 50 games)
# --------------------------------------------------

play_counts = {}
for play in plays:
    game_id = str(play["game_id"])
    play_counts[game_id] = play_counts.get(game_id, 0) + 1

top_games = sorted(play_counts.items(), key=lambda item: item[1], reverse=True)[:50]
pie_rows = [
    {"Game": games_dict[gid]["game_name"], "Plays": count}
    for gid, count in top_games
    if gid in games_dict
]

st.header("Share of Plays (Top 50 Games)")

if pie_rows:
    st.vega_lite_chart(
        pd.DataFrame(pie_rows),
        {
            "mark": {"type": "arc", "tooltip": True},
            "encoding": {
                "theta": {"field": "Plays", "type": "quantitative", "stack": True},
                "color": {"field": "Game", "type": "nominal", "sort": {"field": "Plays", "order": "descending"}},
                "tooltip": [
                    {"field": "Game", "type": "nominal"},
                    {"field": "Plays", "type": "quantitative"},
                ],
            },
        },
        use_container_width=True,
    )
else:
    st.info("No plays recorded yet.")
