CREATE DATABASE SVO;

-- Подключение к базе данных
\c User;

-- Создание таблицы пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL
);


INSERT INTO users (username, password, email)
VALUES
    ('user4', 'password1', 'user1@example.com'),
    ('user56', 'password2', 'user2@example.com'),
    ('user7', 'password3', 'user3@example.com');


SELECT * FROM users;    -- просмотр всей таблицы

-- DELETE FROM users; -- Удаление всей таблицы