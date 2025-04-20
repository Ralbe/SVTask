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
        SELECT Ads.ad_id, Ads.title, Ads.description, Categories.name, Locations.city, Ads.money
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
    
def set_contact(tg_id, name, number):
    """Добавляет нового пользователя в базу данных."""
    cursor.execute(
        """
        INSERT INTO users (tg_id, name, number)
        VALUES (%s, %s, %s)
        ON CONFLICT (tg_id) DO UPDATE SET
        name = EXCLUDED.name,
        number = EXCLUDED.number;
        """,
        (tg_id, name, number))


def insert_new_ad(user_id, category_id, location_id, title, description, price):
    
    cursor.execute("SELECT nextval('ads_ad_id_seq')")
    ad_id = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO Ads (user_id, category_id, location_id, title, description, money)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ad_id
        """,
        (user_id, category_id, location_id, title, description, price)
    )
    return ad_id

def add_category(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Categories(name)
                   VALUES(%s)
                   RETURNING category_id
                   """,
                   (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def add_user_by_tg_id(tg_id):
    """Добавляет пользователя по тг id."""
    cursor.execute("""  
                   INSERT INTO People(name)
                   VALUES(%s)
                   RETURNING user_id
                   """,
                   (tg_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_user_id_by_tg_id(tg_id):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   SELECT COALESCE((
                   SELECT user_id 
                   FROM People
                   WHERE tg_id = %s),
                   0) AS result
                   """,
                   (tg_id,))
    result = cursor.fetchone()
    if result[0]==0 :
        return add_user_by_tg_id(tg_id)
    return result[0] if result else None

def add_category(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Categories(name)
                   VALUES(%s)
                   RETURNING category_id
                   """,
                   (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_category_id(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   SELECT COALESCE((
                   SELECT category_id 
                   FROM Categories 
                   WHERE lower(name) = lower(%s)),
                   0) AS result
                   """,
                   (category_name,))
    result = cursor.fetchone()
    if result[0]==0 :
        return add_category(category_name)
    return result[0] if result else None

def add_location(location_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Locations(city)
                   VALUES(%s)
                   RETURNING location_id
                   """,
                   (location_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_location_id(location_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   SELECT COALESCE((
                   SELECT location_id 
                   FROM Locations
                   WHERE lower(city) = lower(%s)),
                   0) AS result
                   """,
                   (location_name,))
    result = cursor.fetchone()
    if result[0]==0 :
        return add_location(location_name)
    return result[0] if result else None


def close_connection():
    """Закрывает соединение с базой данных."""
    cursor.close()
    conn.close()
