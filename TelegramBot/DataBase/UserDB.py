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

def get_ads():
    """Получает все объявления из базы данных."""
    cursor.execute("""
        SELECT Ads.ad_id, Ads.title, Ads.description, Categories.name, Locations.city, Locations.country
        FROM Ads
        JOIN Categories ON Ads.category_id = Categories.category_id
        JOIN Locations ON Ads.location_id = Locations.location_id
    """)
    return cursor.fetchall()

# cursor.execute("""
#         INSERT INTO Categories (category_id, name) VALUES
#         (1, 'Транспорт'),
#         (2, 'Недвижимость'),
#         (3, 'Работа'),
#         (4, 'Услуги'),
#         (5, 'Личные вещи'),
#         (6, 'Для дома и дачи'),
#         (7, 'Бытовая электроника'),
#         (8, 'Хобби и отдых'),
#         (9, 'Животные'),
#         (10, 'Для бизнеса')
#     """)


# cursor.execute("""
#         INSERT INTO Locations (location_id, city, state, country) VALUES
#         (1, 'Москва', 'Московская область', 'Россия'),
#         (2, 'Санкт-Петербург', NULL, 'Россия'),
#         (3, 'Новосибирск', NULL, 'Россия'),
#         (4, 'Екатеринбург', NULL, 'Россия'),
#         (5, 'Ростов-на-Дону', 'Ростовская область', 'Россия'),
#         (6, 'Минск', NULL, 'Беларусь'),
#         (7, 'Алматы', NULL, 'Казахстан'),
#         (8, 'Нью-Йорк', 'NY', 'США'),
#         (9, 'Лос-Анджелес', 'CA', 'США'),
#         (10, 'Лондон', NULL, 'Великобритания')
#     """)


# cursor.execute("""
#         INSERT INTO Ads (ad_id, user_id, category_id, location_id, title, description) VALUES
#         (1, 1, 1, 1, 'Продам Toyota Camry', '2015 г.в., пробег 100000 км'),
#         (2, 2, 2, 2, 'Сдам 2-комнатную квартиру', 'Центр, 60 кв.м, после ремонта'),
#         (3, 3, 3, 3, 'Продам iPhone 13', 'Новый, в коробке, гарантия')
#     """)
