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


async def get_ads():
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.ad_id,Ads.user_id, Ads.title, Ads.description, Categories.name, Locations.city, Ads.money, Ads.create_date
        FROM Ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
    """)
    return cursor.fetchall()

async def get_ad_by_id(ad_id):
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.user_id, Ads.title, Ads.description, Categories.name, Locations.city, Ads.money, Ads.create_date
        FROM Ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
        WHERE ad_id = %s
    """, (ad_id,))
    return cursor.fetchall()

async def increment_ad_views(ad_id: int):
    cursor.execute(
        "INSERT INTO ad_statistics (ad_id, views) "
        "VALUES (%s, 1) ON CONFLICT (ad_id) "
        "DO UPDATE SET views = ad_statistics.views + 1",
        (ad_id,)
    )

async def get_user_by_email(email):
    """Получает пользователя по email."""
    cursor.execute("SELECT * FROM people WHERE email = %s", (email,))
    return cursor.fetchone()


async def authenticate_user(email, password):
    """Аутентифицирует пользователя по email и паролю."""
    cursor.execute("SELECT * FROM people WHERE email = %s AND password = %s",
                   (email, password))
    return cursor.fetchone()


async def set_user_data(first_name, second_name, phone, email, tg_id):
    """Сохраняет данные пользователя"""
    cursor.execute(
        """
        UPDATE People
        SET firstname = %s,
        secondname = %s,
        phone_number = %s,
        email = %s
        WHERE tg_id = %s
        """,
        (first_name, second_name, phone, email, tg_id))
    
async def get_user_data(tg_id):
    """Возвращает Имя, Фамилию, Номер, Почту"""

    cursor.execute(
        """
        SELECT firstname, secondname, phone_number, email
        FROM People
        WHERE tg_id = %s
        """,(tg_id,)
    )
    return cursor.fetchall()

async def get_user_ads(user_id):
    cursor.execute(
    """
    SELECT ad_id
    FROM ads
    WHERE user_id = %s
    """,(user_id,)
    )
    return cursor.fetchall()
    
async def set_contact(tg_id, name, number):
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


async def insert_new_ad(user_id, category_id, title, description, price, location_id='1'):
    
    # cursor.execute("SELECT nextval('ads_ad_id_seq')")
    # ad_id = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO ads(user_id, category_id, title, description, money, location_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ad_id
        """,
        (user_id, category_id, title, description, price, location_id)
    )
    ad_id = cursor.fetchone()[0]
    return ad_id

async def update_ad(ad_id, user_id, category_id, title, description, price, location_id='1'):
    cursor.execute(
        """
        UPDATE Ads
        SET user_id = %s, category_id = %s, title = %s, description = %s, money = %s, location_id = %s
        WHERE ad_id = %s
        """,
        (user_id, category_id, title, description, price, location_id, ad_id)
    )
    return ad_id

async def add_category(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Categories(name)
                   VALUES(%s)
                   RETURNING category_id
                   """,
                   (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

async def add_user_by_tg_id(tg_id):
    """Добавляет пользователя по тг id."""
    cursor.execute("""  
                   INSERT INTO People(tg_id)
                   VALUES(%s)
                   RETURNING user_id
                   """,
                   (tg_id,))
    result = cursor.fetchone()
    return result[0] if result else None

async def get_user_id_by_tg_id(tg_id):
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

async def add_category(category_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Categories(name)
                   VALUES(%s)
                   RETURNING category_id
                   """,
                   (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None

async def get_category_id(category_name):
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
    # if result[0]==0 :
    #     return add_category(category_name)
    return result[0] if result else None

async def get_categories():
    cursor.execute("""
                   SELECT name
                   FROM Categories
                   ORDER By name
                    """)
    return cursor.fetchall()

async def get_contact_by_ad_id(ad_id):
    cursor.execute("""
                   SELECT firstname, tg_id
                   FROM Ads join people on ads.user_id = people.user_id 
                   WHERE ad_id = %s
                   """,(ad_id,)
    )
    return cursor.fetchall()

async def get_saved_by_user(user_id):
    cursor.execute("""
                   SELECT ad_id
                   FROM saved_ads
                   WHERE user_id =%s
                   """, (user_id,))
    return cursor.fetchall()

async def users_who_saved(ad_id):
    cursor.execute("""
                   SELECT user_id
                   FROM saved_ads
                   WHERE user_id =%s
                   """, (ad_id,))
    return cursor.fetchall()

async def add_ad_in_saved(ad_id, user_id):
    cursor.execute(
        """
        INSERT INTO saved_ads(ad_id, user_id)
        VALUES(%s,%s)
        """, (ad_id, user_id))
    
    cursor.execute(
            """
            UPDATE ad_statistics 
            SET saves = saves + 1 
            WHERE ad_id = %s
            """,
            (ad_id,)
        )
    
async def remove_ad_from_saved(ad_id, user_id):
    cursor.execute(
        """
        DELETE FROM saved_ads
        where ad_id = %s and user_id = %s
        """, (ad_id, user_id))
    cursor.execute(
        """
        UPDATE ad_statistics 
        SET saves = saves -1 
        WHERE ad_id = %s
        """,
        (ad_id,)
    )

async def get_statistic(ad_id: tuple) -> tuple:
    """Возвращает статистику объявления: (просмотры, сохранения)"""
    try:
        cursor.execute(
            "SELECT views, saves FROM ads WHERE ad_id = %s",
            (ad_id[0],)
        )
        result = cursor.fetchone()
        return result if result else (0, 0)  # Возвращаем значения по умолчанию
    except Exception as e:
        # logging.error(f"Error in get_statistic: {e}")
        return (0, 0)  # Возвращаем значения по умолчанию при ошибке

async def add_location(location_name):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   INSERT INTO Locations(city)
                   VALUES(%s)
                   RETURNING location_id
                   """,
                   (location_name,))
    result = cursor.fetchone()
    return result[0] if result else None

async def get_location_id(location_name):
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

async def add_photo(ad_id: int, file_id: str):
    """Добавляет фотографию к объявлению"""

    cursor.execute(
        "INSERT INTO ad_photos (ad_id, file_id) VALUES (%s, %s) RETURNING photo_id",
                (ad_id, file_id)  # Убедитесь, что передается кортеж из 2 элементов
    )
    return cursor.fetchone()[0]

async def get_ad_photos(ad_id: int) -> list:
    """Возвращает список фотографий для объявления"""

    cursor.execute("SELECT file_id FROM ad_photos WHERE ad_id = %s ORDER BY photo_id", (ad_id,))
    return [row[0] for row in cursor.fetchall()]

async def delete_ad_photos(ad_id: int):
    """Удаляет все фотографии объявления"""

    cursor.execute("DELETE FROM ad_photos WHERE ad_id = %s", (ad_id,))

def close_connection():
    """Закрывает соединение с базой данных."""
    cursor.close()
    conn.close()
