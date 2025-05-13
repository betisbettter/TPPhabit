import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from db import get_connection
from habit_logic import get_habits_for_date, total_days, CHALLENGE_START, CHALLENGE_END
import calplot

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


# Create calendar heatmap data
def get_daily_completion_df(user_id):
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
            expected_count = day_num
            completion_rate = len(completed_habits) / expected_count
            completion_by_date[log_date] = completion_rate

    # Build calendar series with 0% for missing days
    full_range = pd.date_range(CHALLENGE_START, CHALLENGE_END)
    calendar_series = pd.Series({
        d.date(): completion_by_date.get(d.date(), 0.0)
        for d in full_range
    })

    return calendar_series


# Main dashboard view
def show_dashboard(user_id):
    st.subheader("📆 Your Daily Habit Tracker")

    today = date.today()
    if today < CHALLENGE_START or today > CHALLENGE_END:
        st.warning("This challenge is not currently active.")
        return

    # Date selector
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

    # Load habit log for selected day
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

    # Pie Chart for adherence
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
        st.info("No logs yet. Start submitting habits!")

    # Calendar Heatmap
    # Calendar Heatmap
    st.markdown("### 📅 Daily Completion Calendar")

    calendar_series = get_daily_completion_df(user_id)

    fig_cal, ax_cal = calplot.calplot(
        calendar_series,
        cmap="YlGn",
        suptitle="Your Daily Completion Rates",
        colorbar=True,
        edgecolor="white",
        linewidth=1,
        textformat="{:.0%}",
        how="sum",
        yearlabels=False,
        monthlabels=("May", "June"),
        daylabels="MTWTFSS",
        figsize=(14, 3),
        tight_layout=True
    )

    st.pyplot(fig_cal)


    # Historical Log Table
    st.markdown("### 🗂️ Habit Log History")
    if not full_df.empty:
        st.dataframe(full_df[::-1], use_container_width=True)
    else:
        st.write("No habit logs yet.")
