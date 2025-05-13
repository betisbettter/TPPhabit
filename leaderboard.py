# leaderboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_connection

def get_leaderboard_data():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username, SUM(array_length(h.completed_habits, 1)) as total_completed
            FROM users u
            JOIN habit_logs h ON u.id = h.user_id
            GROUP BY u.username
            ORDER BY total_completed DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Username", "Total Habits Completed"])

def show_leaderboard():
    st.subheader("Top 10")

    df = get_leaderboard_data()

    if df.empty:
        st.info("No data yet — encourage users to start logging habits!")
        return

    # Display table
    st.dataframe(df, use_container_width=True)

    # Bar chart
    fig, ax = plt.subplots()
    ax.barh(df["Username"], df["Total Habits Completed"], color="#4CAF50")
    ax.set_xlabel("Habits Completed")
    ax.invert_yaxis()
    st.pyplot(fig)
