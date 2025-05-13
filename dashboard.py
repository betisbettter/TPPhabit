import streamlit as st
import pandas as pd
from datetime import datetime, date
from db import get_connection
from habit_logic import get_habits_for_date, total_days, CHALLENGE_START, CHALLENGE_END
import matplotlib.pyplot as plt

def get_user_progress(user_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT date, completed_habits FROM habit_logs WHERE user_id = %s ORDER BY date ASC", (user_id,))
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["Date", "Completed Habits"])

def save_user_habits(user_id, target_date, completed_habits):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO habit_logs (user_id, date, completed_habits)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, date) DO UPDATE SET completed_habits = EXCLUDED.completed_habits
        """, (user_id, target_date, completed_habits))
        conn.commit()

from datetime import datetime

def calculate_adherence(df):
    total_possible = 0
    total_completed = 0

    for _, row in df.iterrows():
        raw_date = row["Date"]
        # Ensure date is a Python date object
        if isinstance(raw_date, str):
            challenge_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        elif isinstance(raw_date, pd.Timestamp):
            challenge_date = raw_date.date()
        else:
            challenge_date = raw_date  # already a date

        day_number = (challenge_date - CHALLENGE_START).days + 1
        total_possible += day_number
        total_completed += len(row["Completed Habits"])

    return total_completed, total_possible


def show_dashboard(user_id):
    st.subheader("📆 Your Daily Habit Tracker")

    today = date.today()
    if today < CHALLENGE_START or today > CHALLENGE_END:
        st.warning("This challenge is not currently active.")
        return

    day_of_challenge = (today - CHALLENGE_START).days + 1
    today_habits = get_habits_for_date(today)

    st.markdown(f"### Day {day_of_challenge}: {today.strftime('%B %d, %Y')}")
    st.markdown("Check off the habits you completed today:")

    # Get current data
    existing_df = get_user_progress(user_id)
    existing_today = existing_df[existing_df["Date"] == pd.to_datetime(today)]

    completed_today = []
    for habit in today_habits:
        default = habit in (existing_today["Completed Habits"].iloc[0] if not existing_today.empty else [])
        if st.checkbox(habit, value=default, key=habit):
            completed_today.append(habit)

    if st.button("Submit Today's Habits"):
        save_user_habits(user_id, today, completed_today)
        st.success("Habits saved!")
        st.experimental_rerun()

    # Display Adherence Pie Chart
    st.markdown("---")
    st.markdown("### 📊 Your Progress So Far")
    full_df = get_user_progress(user_id)

    if not full_df.empty:
        total_completed, total_possible = calculate_adherence(full_df)
        percent = round(100 * total_completed / total_possible, 1) if total_possible > 0 else 0

        fig, ax = plt.subplots()
        ax.pie([total_completed, total_possible - total_completed],
               labels=["Completed", "Missed"],
               autopct="%1.1f%%",
               startangle=90,
               colors=["#4CAF50", "#FF5722"])
        ax.axis("equal")
        st.pyplot(fig)

        st.markdown(f"**{total_completed} / {total_possible} habits completed** ({percent}%)")
    else:
        st.info("No habits logged yet. Start by submitting today's habits above.")

    st.markdown("### 📅 Daily Completion Calendar")

    calendar_series = get_daily_completion_df(user_id)

    fig_cal, ax_cal = calplot.calplot(
        calendar_series,
        cmap="YlGn",
        suptitle="Your Daily Completion Rates",
        colorbar=True,
        edgecolor="white",
        linewidth=1,
        textformat="{:.0%}"
    )

    st.pyplot(fig_cal)




    # Show historical logs
    st.markdown("### 🗂️ Habit Log History")
    if not full_df.empty:
        st.dataframe(full_df[::-1], use_container_width=True)
    else:
        st.write("No habit logs yet.")



