import bcrypt
import psycopg2
from db import get_connection

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username, password, recovery_q, recovery_a):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (username, password_hash, recovery_question, recovery_answer) VALUES (%s, %s, %s, %s)",
                    (username, hash_password(password), recovery_q, recovery_a))
        conn.commit()
