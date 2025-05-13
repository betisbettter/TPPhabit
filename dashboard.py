import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date, timedelta
from db import get_connection
from habit_logic import get_habits_for_date, total_days, CHALLENGE_START, CHALLENGE_END

# Load user progress
def get_user_progress(user_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT date, completed_habits FROM habit_logs WHERE user_id = %s ORDER BY date ASC", (user_id,))
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Date", "Completed Habits"])

# Save progress to DB
def save_user_habits(user_id, target_date, completed_habits):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO habit_logs (user_id, date, completed_habits)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, date) DO UPDATE SET completed_habits = EXCLUDED.completed_habits
        """, (user_id, target_date, completed_habits))
        conn.commit()

# Calculate adherence stats
def calculate_adherence(df):
    total_possible = 0
    total_completed = 0

    for _, row in df.iterrows():
        raw_date = row["Date"]
        if isinstance(raw_date, str):
            challenge_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        elif isinstance(raw_date, pd.Timestamp):
            challenge_date = raw_date.date()
        else:
            challenge_date = raw_date

        # Skip future days
        if challenge_date > date.today():
            continue

        day_number = (challenge_date - CHALLENGE_START).days + 1
        total_possible += day_number
        total_completed += len(row["Completed Habits"])

    return total_completed, total_possible

# Build data matrix for calendar heatmap
def get_weekday_heatmap_data(user_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT date, completed_habits FROM habit_logs
            WHERE user_id = %s ORDER BY date ASC
        """, (user_id,))
        data = cur.fetchall()

    completion_by_date = {}
    for log_date, completed_habits in data:
        if CHALLENGE_START <= log_date <= CHALLENGE_END:
            day_num = (log_date - CHALLENGE_START).days + 1
            expected = day_num
            pct = len(completed_habits) / expected if expected > 0 else 0
            completion_by_date[log_date] = pct

    num_days = (CHALLENGE_END - CHALLENGE_START).days + 1
    data_matrix = np.full((7, 7), np.nan)
    annot_matrix = [["" for _ in range(7)] for _ in range(7)]

    for i in range(num_days):
        d = CHALLENGE_START + timedelta(days=i)
        week_idx = (d - CHALLENGE_START).days // 7
        day_idx = (d.weekday() + 2) % 7  # ✅ Saturday = 0

        pct = completion_by_date.get(d, 0.0)
        data_matrix[week_idx][day_idx] = pct
        annot_matrix[week_idx][day_idx] = f"{d.strftime('%m/%d')}\n{int(pct*100)}%"

    return data_matrix, annot_matrix

# Main dashboard view
def show_dashboard(user_id):
    st.subheader("🏋️ Your Daily Habit Tracker")

    today = date.today()
    if today < CHALLENGE_START or today > CHALLENGE_END:
        st.warning("This challenge is not currently active.")
        return

    selected_date = st.date_input(
        "Select a date to view or update habits:",
        min_value=CHALLENGE_START,
        max_value=min(today, CHALLENGE_END),
        value=today
    )

    day_of_challenge = (selected_date - CHALLENGE_START).days + 1
    habits_for_day = get_habits_for_date(selected_date)

    st.markdown(f"### Day {day_of_challenge}: {selected_date.strftime('%B %d, %Y')}")
    st.markdown("Check off the habits you completed:")

    existing_df = get_user_progress(user_id)
    existing_entry = existing_df[existing_df["Date"] == pd.to_datetime(selected_date)]

    completed = []
    for habit in habits_for_day:
        default = habit in (existing_entry["Completed Habits"].iloc[0] if not existing_entry.empty else [])
        if st.checkbox(habit, value=default, key=f"{selected_date}-{habit}"):
            completed.append(habit)

    if st.button("Save Habits"):
        save_user_habits(user_id, selected_date, completed)
        st.success("Habits saved!")
        st.rerun()

    full_df = get_user_progress(user_id)


    # Heatmap Calendar
    st.markdown("### 📅 Daily Completion Calendar")

    data_matrix, annot_matrix = get_weekday_heatmap_data(user_id)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(
        data_matrix,
        cmap="YlGn",
        annot=annot_matrix,
        fmt="",
        cbar=True,
        linewidths=0.5,
        linecolor='gray',
        xticklabels=["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"],
        yticklabels=[f"Week {i+1}" for i in range(7)],
        ax=ax
    )

    ax.set_title("Your Daily Completion Calendar (Date & %)")
    st.pyplot(fig)


    # Historical Log Table
    st.markdown("### 🗂️ Habit Log History")
    if not full_df.empty:
        st.dataframe(full_df[::-1], use_container_width=True)
    else:
        st.write("No habit logs yet.")


    # Logout Button
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.rerun()
    
