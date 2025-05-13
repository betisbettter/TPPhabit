import streamlit as st
import pandas as pd
from datetime import datetime
from db import get_connection
from habit_logic import get_habits_for_day

def get_user_progress(user_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT date, completed_habits FROM habit_logs WHERE user_id = %s ORDER BY date ASC", (user_id,))
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Date", "Completed Habits"])

def save_user_habits(user_id, date, completed_habits):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO habit_logs (user_id, date, completed_habits)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, date) DO UPDATE SET completed_habits = EXCLUDED.completed_habits
        """, (user_id, date, completed_habits))
        conn.commit()

def show_dashboard(user_id):
    st.subheader("📆 Your Daily Habit Tracker")

    today = datetime.today().date()
    start_date = datetime(today.year, today.month, 1).date()  # Example: fixed start date (can be dynamic later)
    day_of_challenge = (today - start_date).days + 1

    if day_of_challenge < 1 or day_of_challenge > 30:
        st.warning("This challenge is not currently active.")
        return

    st.markdown(f"### Day {day_of_challenge} - {today.strftime('%B %d')}")
    today_habits = get_habits_for_day(day_of_challenge)

    # Get current habits logged for today (if any)
    existing_df = get_user_progress(user_id)
    existing_today = existing_df[existing_df["Date"] == pd.to_datetime(today)]

    # Habit checkboxes
    st.markdown("#### Select completed habits for today:")
    completed = []
    for habit in today_habits:
        default = False
        if not existing_today.empty and habit in existing_today["Completed Habits"].iloc[0]:
            default = True
        if st.checkbox(habit, value=default):
            completed.append(habit)

    if st.button("Submit Today's Habits"):
        save_user_habits(user_id, today, completed)
        st.success("Habits saved!")
        st.experimental_rerun()

    # Display past logs
    st.markdown("---")
    st.markdown("### 🗂️ Your Habit History")
    progress_df = get_user_progress(user_id)

    if not progress_df.empty:
        st.dataframe(progress_df[::-1], use_container_width=True)
    else:
        st.info("No habit logs found yet.")
