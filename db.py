# db.py
import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(
        st.secrets["database"]["url"],
        sslmode="require"
    )
