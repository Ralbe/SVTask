import psycopg2

DB_NAME = "info_users"
DB_HOST = "127.0.0.1"
DB_USER = "postgres"
DB_PASSWORD = "33772"
DB_PORT = "5432"

# Подключение к базе данных
conn = psycopg2.connect(dbname=DB_NAME, host=DB_HOST, user=DB_USER,
                        password=DB_PASSWORD, port=DB_PORT)
cursor = conn.cursor()
conn.autocommit = True

def get_ads():
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.ad_id, Ads.title, Ads.description, Categories.name, Locations.city, Locations.country, Ads.money
        FROM Ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
    """)
    return cursor.fetchall()


def get_user_by_email(email):
    """Получает пользователя по email."""
    cursor.execute("SELECT * FROM people WHERE email = %s", (email,))
    return cursor.fetchone()


def authenticate_user(email, password):
    """Аутентифицирует пользователя по email и паролю."""
    cursor.execute("SELECT * FROM people WHERE email = %s AND password = %s",
                   (email, password))
    return cursor.fetchone()


def add_user(login, password, email):
    """Добавляет нового пользователя в базу данных."""
    cursor.execute(
        "INSERT INTO people (username, password, email) VALUES (%s, %s, %s)",
        (login, password, email))


def insert_new_ad(user_id, category_id, location_id, title, description, price):
    cursor.execute(
        """
        INSERT INTO Ads (user_id, category_id, location_id, title, description, money)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ad_id
        """,
        (user_id, category_id, location_id, title, description, price)
    )
    ad_id = cursor.fetchone()[0]
    return ad_id


def get_category_id(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("SELECT category_id FROM Categories WHERE name = %s",
                   (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_location_id(location_name):
    """Получает идентификатор местоположения по названию города."""
    cursor.execute("SELECT location_id FROM Locations WHERE city = %s",
                   (location_name.split()[0],))
    result = cursor.fetchone()
    return result[0] if result else None


def close_connection():
    """Закрывает соединение с базой данных."""
    cursor.close()
    conn.close()
