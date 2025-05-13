import streamlit as st
from auth import register_user, check_password, hash_password
from db import get_connection
from dashboard import show_dashboard
from leaderboard import show_leaderboard

st.set_page_config(page_title="30-Day Habit Challenge", layout="centered")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""

def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password(password, user[1]):
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup():
    st.header("Sign Up")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    recovery_q = st.text_input("Recovery Question")
    recovery_a = st.text_input("Answer")

    if st.button("Register"):
        try:
            register_user(username, password, recovery_q, recovery_a)
            st.success("User registered! Please log in.")
        except Exception as e:
            st.error(f"Registration failed: {e}")

def main_menu():
    st.sidebar.title("Menu")
    choice = st.sidebar.radio("Go to", ["Dashboard", "Leaderboard", "Logout"])

    if choice == "Dashboard":
        show_dashboard(st.session_state.user_id)
    elif choice == "Leaderboard":
        show_leaderboard()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = ""
        st.rerun()

def main():
    st.title("🏋️ 30-Day Habit Challenge App")

    if st.session_state.logged_in:
        main_menu()
    else:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login()
        with tab2:
            signup()

if __name__ == "__main__":
    main()
