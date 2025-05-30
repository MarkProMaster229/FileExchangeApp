import psycopg2
from psycopg2 import sql

class UserRegistration:
    def __init__(self, host='localhost', database='mydatabase', user='myuser', password='mypassword'):
        self.conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            self.conn.commit()

    def get_user(self, username):
        with self.conn.cursor() as cur:
            cur.execute("SELECT username, password FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            if result:
                return {"username": result[0], "password": result[1]}
            return None

    def add_user(self, username, password):
        with self.conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                self.conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                self.conn.rollback()
                return False

    def close(self):
        self.conn.close()


#version: '3.8'

#services:
  #postgres:
    #image: postgres:16
    #container_name: postgres_db
    #environment:
      #POSTGRES_DB: mydatabase
      #POSTGRES_USER: myuser
      #POSTGRES_PASSWORD: mypassword
    #ports:
      #- "5432:5432"
    #volumes:
      #- pgdata:/var/lib/postgresql/data

#volumes:
  #pgdata:
