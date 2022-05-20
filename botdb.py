import sqlite3
import os
import json
from config import NoHistoryError
from datetime import date, datetime
from collections.abc import Iterable


def is_db_exists(db_name: str) -> bool:
    """
    Функция, которая проверяет существет ли база данных в файле, название которого получено от пользователя.

    :param db_name: Название файла базы данных.
    :return: Возвращает значение True или False.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, db_name)
    if os.path.isfile(db_path):
        if os.path.getsize(db_path) > 100:
            with open(db_path, 'r', encoding="ISO-8859-1") as f:
                header = f.read(100)
                if header.startswith('SQLite format 3'):
                    return True
    return False


def create_db(db_name: str) -> None:
    """
    Функция, которая создаёт базу данных.

    :param db_name: Название файла базы данных.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, db_name)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS bot_history (
                    num_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_id TEXT NOT NULL,
                    city TEXT NOT NULL,
                    city_id INTEGER NOT NULL,
                    checkin DATE NOT NULL,
                    checkout DATE NOT NULL,
                    command TEXT NOT NULL,
                    command_time DATETIME NOT NULL,
                    results TEXT)""")
        conn.commit()


def insert(user_id: int, city: str, city_id: int, checkin: date, checkout: date, command: str, command_time: datetime, results: str) -> None:
    """
    Функция, которая записывает полученные от пользователя значения в базу данных.

    :param user_id: id пользователя.
    :param city: Название города.
    :param city_id: id города.
    :param checkin: Дата заезда в отель.
    :param checkout: Дата отъезда из отеля.
    :param command: Название команды, вызванной пользователем.
    :param command_time: Дата и время вода команды.
    :param results: Список с параметрами отелей.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'bot_database.db')
    hotels = json.dumps(results)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bot_history (user_id, city, city_id, checkin, checkout, command, command_time, results) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, city, city_id, checkin, checkout, command, command_time, hotels))
        conn.commit()


def fetch_by_id(id: int, db_name: str) -> Iterable[tuple]:
    """
    Функция, которая обращается к базе данных для поиска истории пользователя и
    генерирует кортеж с результатами.

    В случае если у пользователя история не найдена, вызывается исключение "NoHistoryError",
    которое обрабатывается в основной функции.

    :param id: id пользователя.
    :param db_name: Название файла базы данных.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, db_name)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bot_history WHERE user_id=?", [id])
        all_results = cur.fetchall()
        if all_results:
            for entry in all_results:
                yield 'Команда: ', entry[6],\
                      'Дата и время поиска: ', entry[7],\
                      json.loads(entry[8])
        else:
            raise NoHistoryError
