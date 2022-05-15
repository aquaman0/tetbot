import sqlite3
import os
import json
from config import NoHistoryError


def insert(user_id, city, city_id, checkin, checkout, command, command_time, results):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'bot_database.db')
    hotels = json.dumps(results)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bot_history (user_id, city, city_id, checkin, checkout, command, command_time, results) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, city, city_id, checkin, checkout, command, command_time, hotels))
        conn.commit()


def fetch_by_id(id):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'bot_database.db')
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
