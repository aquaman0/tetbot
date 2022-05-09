import sqlite3


class dbAccess:

    def __init__(self):
        self.db_name = 'users_database.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        if exc_val:
            raise ValueError
    #
    #
    #
    # with dbAccess() as data:
    #     cur = data.cursor()
    #     cur.execute("""CREATE TABLE IF NOT EXISTS users_query(
    #        userid INT PRIMARY KEY,
    #        city TEXT,
    #        city_id TEXT,
    #        checkin TEXT,
    #        checkout TEXT,
    #        hotelsQty INT);
    #     """)
    #     data.commit()
    #
    # with dbAccess() as data:
    #     cur = data.cursor()
    #     cur.execute("INSERT or REPLACE INTO users VALUES(?, ?)", (message.from_user.id, message.from_user.first_name))
    #     data.commit()
    #
    #         with dbAccess() as data:
    #             cur = data.cursor()
    #             cur.execute("INSERT or REPLACE INTO users_query VALUES(?, ?, ?, ?, ?, ?)",
    #                         (message.from_user.id, f'{i_city}', f'{city_id}', 'a', 'a', 0))
    #             data.commit()
    # with dbAccess() as data:
    #     cur = data.cursor()
    #     cur.execute("SELECT * FROM users_query;")
    #     all_results = cur.fetchall()