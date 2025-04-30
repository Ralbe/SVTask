import psycopg2

# DB_NAME = "info_users"
# DB_HOST = "127.0.0.1"
# DB_USER = "postgres"
# DB_PASSWORD = "33772"
# DB_PORT = "5432"

DB_NAME = "site_db"
DB_HOST = "127.0.0.1"
DB_USER = "postgres"
DB_PASSWORD = "33772"
DB_PORT = "5432"

# Подключение к базе данных
conn = psycopg2.connect(dbname=DB_NAME, host=DB_HOST, user=DB_USER,
                        password=DB_PASSWORD, port=DB_PORT)
cursor = conn.cursor()
conn.autocommit = True



def get_ad_by_id(ad_id):
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.user_id, Ads.title, Ads.description, Categories.name, 
                Locations.city, Ads.price, Ads.create_date
        FROM main_advertisement ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
        WHERE ad_id = %s
    """, (ad_id,))
    return cursor.fetchall()

def get_ads():
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.ad_id,Ads.user_id, Ads.title, Ads.description, Categories.name, Locations.city, Ads.price, Ads.create_date
        FROM main_advertisement ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
    """)
    return cursor.fetchall()

def increment_ad_views(ad_id: int):
    cursor.execute(
        "INSERT INTO ad_statistics (ad_id, views) "
        "VALUES (%s, 1) ON CONFLICT (ad_id) "
        "DO UPDATE SET views = ad_statistics.views + 1",
        (ad_id,)
    )

def get_user_by_email(email):
    """Получает пользователя по email."""
    cursor.execute("SELECT * FROM accounts_customuser WHERE email = %s", (email,))
    return cursor.fetchone()


def authenticate_user(email, password):
    """Аутентифицирует пользователя по email и паролю."""
    cursor.execute("SELECT * FROM accounts_customuser WHERE email = %s AND password = %s",
                   (email, password))
    return cursor.fetchone()


def set_user_data(firstname, lastname, phone, email, tg_id):
    """Сохраняет данные пользователя"""
    cursor.execute(
        """
        UPDATE accounts_customuser
        SET firstname = %s,
        lastname = %s,
        phone = %s,
        email = %s
        WHERE tg_id = %s
        """,
        (firstname, lastname, phone, email, tg_id))
    
def get_user_data(tg_id):
    """Возвращает Имя, Фамилию, Номер, Почту"""

    cursor.execute(
        """
        SELECT firstname, lastname, phone, email
        FROM accounts_customuser
        WHERE tg_id = %s
        """,(tg_id,)
    )
    return cursor.fetchall()

def get_user_ads(user_id):
    cursor.execute(
    """
    SELECT ad_id
    FROM main_advertisement ads
    WHERE user_id = %s
    """,(user_id,)
    )
    return cursor.fetchall()
    
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


def insert_new_ad(user_id, category_id, title, description, price, location_id='1'):
    
    # cursor.execute("SELECT nextval('ads_ad_id_seq')")
    # ad_id = cursor.fetchone()[0]
    cursor.execute(
        """
        INSERT INTO main_advertisement(user_id, category_id, title, description, price, location_id, count_views)
        VALUES (%s, %s, %s, %s, %s, %s, 0)
        RETURNING ad_id
        """,
        (user_id, category_id, title, description, price, location_id)
    )
    ad_id = cursor.fetchone()[0]
    return ad_id

def update_ad(ad_id, user_id, category_id, title, description, price, location_id='1'):
    cursor.execute(
        """
        UPDATE Ads
        SET user_id = %s, category_id = %s, title = %s, description = %s, price = %s, location_id = %s
        WHERE ad_id = %s
        """,
        (user_id, category_id, title, description, price, location_id, ad_id)
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
                   INSERT INTO accounts_customuser(tg_id, is_superuser)
                   VALUES(%s, False)
                   RETURNING id
                   """,
                   (tg_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_user_id_by_tg_id(tg_id):
    """Получает идентификатор категории по названию."""
    cursor.execute("""
                   SELECT COALESCE((
                   SELECT id
                   FROM accounts_customuser
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
    # if result[0]==0 :
    #     return add_category(category_name)
    return result[0] if result else None

def get_categories():
    cursor.execute("""
                   SELECT name
                   FROM Categories
                   ORDER By name
                    """)
    return cursor.fetchall()

def get_contact_by_ad_id(ad_id):
    cursor.execute("""
                   SELECT firstname, lastname, tg_id, phone
                   FROM main_advertisement ads join accounts_customuser on ads.user_id = accounts_customuser.id 
                   WHERE ad_id = %s
                   """,(ad_id,)
    )
    return cursor.fetchall()

def get_contact_by_user_id(user_id):
    cursor.execute("""
                   SELECT firstname, username, tg_id, phone
                   FROM accounts_customuser
                   WHERE user_id = %s
                   """,(user_id,)
    )
    return cursor.fetchall()

def get_saved_by_user(user_id):
    cursor.execute("""
                   SELECT ad_id
                   FROM main_favoriteadvertisement
                   WHERE user_id =%s
                   """, (user_id,))
    return cursor.fetchall()

def users_who_saved(ad_id):
    cursor.execute("""
                   SELECT user_id
                   FROM main_favoriteadvertisement
                   WHERE user_id =%s
                   """, (ad_id,))
    return cursor.fetchall()

def add_ad_in_saved(ad_id, user_id):
    cursor.execute(
        """
        INSERT INTO main_favoriteadvertisement(ad_id, user_id)
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
    
def remove_ad_from_saved(ad_id, user_id):
    cursor.execute(
        """
        DELETE FROM main_favoriteadvertisement
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

def get_statistic(ad_id):
    """Возвращает статистику объявления: (просмотры, сохранения)"""
    try:
        cursor.execute(
            "SELECT views, saves FROM ad_statistics WHERE ad_id = %s",
            (ad_id,)
        )
        result =  cursor.fetchone()
        return result if result else (0, 0)  # Возвращаем значения по умолчанию
    except Exception as e:
        # logging.error(f"Error in get_statistic: {e}")
        return (0, 0)  # Возвращаем значения по умолчанию при ошибке

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

def add_photo(ad_id: int, file_id: str):
    """Добавляет фотографию к объявлению"""

    cursor.execute(
        "INSERT INTO ad_photos (ad_id, file_id) VALUES (%s, %s) RETURNING photo_id",
                (ad_id, file_id)  # Убедитесь, что передается кортеж из 2 элементов
    )
    return cursor.fetchone()[0]

def get_ad_photos(ad_id: int) -> list:
    """Возвращает список фотографий для объявления"""

    cursor.execute("SELECT file_id FROM ad_photos WHERE ad_id = %s ORDER BY photo_id", (ad_id,))
    return [row[0] for row in cursor.fetchall()]

def delete_ad_photos(ad_id: int):
    """Удаляет все фотографии объявления"""

    cursor.execute("DELETE FROM ad_photos WHERE ad_id = %s", (ad_id,))

# Вакансии
def get_vacancies():
    """Получить все вакансии"""
    
    cursor.execute("""
        SELECT v.ad_id, u.firstname || ' ' || u.lastname as author, 
                v.title, v.description, v.salary, v.requirements, v.contacts, v.created_at, v.user_id
        FROM main_vacation v
        JOIN accounts_customuser u ON v.user_id = u.id
        ORDER BY v.created_at DESC
    """)
    return cursor.fetchall()

def insert_new_vacancy(user_id, title, description, salary, requirements, contacts):
    """Добавить новую вакансию"""
    
    cursor.execute("""
        INSERT INTO main_vacation (user_id, title, description, salary, requirements, contacts, count_views)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING ad_id
    """, (user_id, title, description, salary, requirements, contacts, 0))
    return cursor.fetchone()[0]

def get_vacancy_by_id(ad_id):
    """Получить вакансию по ID"""

    cursor.execute("SELECT * FROM main_vacation WHERE ad_id = %s", (ad_id,))
    return cursor.fetchone()

def get_user_vacancies(user_id):
    """Получить вакансии пользователя"""
    
    cursor.execute("SELECT ad_id FROM main_vacation WHERE user_id = %s", (user_id,))
    return cursor.fetchall()

def update_vacancy(ad_id, title, description, salary, requirements, contacts):
    """Обновить вакансию"""
    
    cursor.execute("""
        UPDATE main_vacation
        SET title = %s, description = %s, salary = %s, requirements = %s, contacts = %s
        WHERE ad_id = %s
    """, (title, description, salary, requirements, contacts, ad_id))

def delete_vacancy(ad_id):
    """Удалить вакансию"""
    
    cursor.execute("DELETE FROM main_vacation WHERE ad_id = %s", (ad_id,))

def get_vacancy_statistics(ad_id):
    """Получить статистику вакансии (просмотры, сохранения)"""
    
    cursor.execute("""
        SELECT views, saves FROM vacancy_stats WHERE ad_id = %s
    """, (ad_id,))
    return cursor.fetchone() or (0, 0)

def increment_vacancy_views(ad_id):
    """Увеличить счетчик просмотров"""
    
    cursor.execute("""
        INSERT INTO vacancy_stats (ad_id, views, saves)
        VALUES (%s, 1, 0)
        ON CONFLICT (ad_id) DO UPDATE SET views = vacancy_stats.views + 1
    """, (ad_id,))

def get_saved_vacancies(user_id):
    """Получить сохранённые вакансии пользователя"""
    
    cursor.execute("SELECT ad_id FROM saved_vacancies WHERE user_id = %s", (user_id,))
    return cursor.fetchall()

def add_vacancy_to_saved(ad_id, user_id):
    """Добавить вакансию в сохранённые"""
    
    cursor.execute("""
        INSERT INTO saved_vacancies (user_id, ad_id) VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, ad_id))
    cursor.execute("""
        UPDATE vacancy_stats SET saves = saves + 1 WHERE ad_id = %s
    """, (ad_id,))

def remove_vacancy_from_saved(ad_id, user_id):
    """Удалить вакансию из сохранённых"""
    
    cursor.execute("DELETE FROM saved_vacancies WHERE user_id = %s AND ad_id = %s", (user_id, ad_id))
    cursor.execute("""
        UPDATE vacancy_stats SET saves = saves - 1 WHERE ad_id = %s
    """, (ad_id,))

def close_connection():
    """Закрывает соединение с базой данных."""
    cursor.close()
    conn.close()
