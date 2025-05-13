import streamlit as st
from auth import register_user, check_password, hash_password
from db import get_connection
from dashboard import show_dashboard
from leaderboard import show_leaderboard
from PIL import Image

st.set_page_config(page_title="RELENTL45S", layout="centered")

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

    # --- Forgot Password Flow ---
    with st.expander("Forgot Password?"):
        recovery_user = st.text_input("Enter your username to recover password", key="recovery_username")

        if st.button("Start Recovery"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT recovery_question FROM users WHERE username = %s", (recovery_user,))
            result = cur.fetchone()
            conn.close()

            if result:
                st.session_state.recovery_user = recovery_user
                st.session_state.recovery_question = result[0]
                st.session_state.recovery_mode = True
                st.rerun()
            else:
                st.error("Username not found.")

    # Step 2: Answer recovery question
    if st.session_state.get("recovery_mode") and st.session_state.get("recovery_user"):
        st.info(f"Recovery Question: {st.session_state.recovery_question}")
        recovery_answer = st.text_input("Answer to recovery question", type="password", key="recovery_answer")

        if st.button("Verify Recovery Answer"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id FROM users
                WHERE username = %s AND recovery_answer = %s
            """, (st.session_state.recovery_user, recovery_answer))
            result = cur.fetchone()
            conn.close()

            if result:
                st.session_state.recovery_verified = True
                st.success("Recovery answer verified. Please set a new password.")
                st.rerun()
            else:
                st.error("Incorrect answer to recovery question.")

    # Step 3: Let user reset password
    if st.session_state.get("recovery_verified"):
        new_password = st.text_input("Enter new password", type="password")
        confirm_password = st.text_input("Confirm new password", type="password")

        if st.button("Reset Password"):
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 4:
                st.warning("Password should be at least 4 characters.")
            else:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    UPDATE users
                    SET password_hash = %s
                    WHERE username = %s
                """, (hash_password(new_password), st.session_state.recovery_user))
                conn.commit()
                conn.close()

                # Clear recovery state
                st.session_state.recovery_mode = False
                st.session_state.recovery_verified = False
                st.success("Password reset successfully! You can now log in.")


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
    with st.expander("📆 Dashboard", expanded=True):
        show_dashboard(st.session_state.user_id)

    with st.expander("🏆 Leaderboard", expanded=False):
        show_leaderboard()


def main():
  
    st.markdown(
            """
            <div style='display: flex; align-items: center; height: 100%;'>
                <h1 style='color:MediumSeaGreen;'>RELENTL45S</h1>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.image("image.png", use_container_width=True)

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
