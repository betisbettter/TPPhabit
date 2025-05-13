# calendar.py

import streamlit as st
import pandas as pd
from datetime import date
from db import get_connection
from habit_logic import CHALLENGE_START, CHALLENGE_END

def get_user_daily_completion(user_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT date, completed_habits FROM habit_logs
            WHERE user_id = %s
            ORDER BY date ASC
        """, (user_id,))
        data = cur.fetchall()
    return pd.DataFrame(data, columns=["Date", "Completed Habits"])

def show_calendar(user_id):
    st.subheader("🗓️ Completion Calendar")

    df = get_user_daily_completion(user_id)
    if df.empty:
        st.info("No habit logs yet.")
        return

    # Calculate percent complete per day
    calendar_data = []
    for _, row in df.iterrows():
        this_date = row["Date"]
        day_index = (this_date - CHALLENGE_START).days + 1
        expected = day_index
        completed = len(row["Completed Habits"])
        percent = round(100 * completed / expected, 1)
        calendar_data.append({
            "Date": this_date,
            "Percent": percent
        })

    df_calendar = pd.DataFrame(calendar_data)

    # Use bar chart as placeholder — calendar heatmap coming soon
    st.bar_chart(df_calendar.set_index("Date")["Percent"])

    # Optional future: build a true heatmap with calplot or plotly
