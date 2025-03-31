import psycopg2


DB_NAME = "info_users"
DB_HOST = "127.0.0.1"
DB_USER = "postgres"
DB_PASSWORD = "33772"
DB_PORT = "5432"

# Подключение к базе данных
conn = psycopg2.connect(dbname=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)
cursor = conn.cursor()
conn.autocommit = True

cursor.close()
conn.close()