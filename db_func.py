import sqlite3


class BotDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def user_exists(self, id_user):

        result = self.cur.execute("SELECT `id` \
                                  FROM `users` \
                                  WHERE `id` = ?", (id_user,))
        return bool(len(result.fetchall()))
    
    def rule_exists(self, id_user):
        result = self.cur.execute("SELECT `rule` \
                                  FROM `users` \
                                  WHERE `id` = ?", (id_user,))
        return result.fetchone()[0] != None
    
    def add_new_text(self, name: str):
        self.cur.execute("INSERT INTO `message_texts` \
                         (`name`) VALUES (?)", (name,))
        return self.conn.commit()

    def add_new_reason(self, id_user: str, reason: str, id_owner_reason: str, date: str, num):
        self.cur.execute("INSERT INTO `history_reasons` (id, reason, owner_reason, date, num) VALUES (?, ?, ?, ?, ?)", (id_user, reason, id_owner_reason, date, num))
        return self.conn.commit()

    def add_new_button(self, name: str):
        self.cur.execute("INSERT INTO `button_texts` \
                         (`name`) VALUES (?)", (name,))
        return self.conn.commit()
    
    def add_user(self, id_user):  # Добавляем юзера в базу
        self.cur.execute("INSERT INTO `users` \
                         (`id`) VALUES (?)", (id_user,))
        return self.conn.commit()

    def add_value(self, key: str, where: str, meaning: str, table: str = 'users', value: str = 0):

        result = self.cur.execute(f"SELECT {key}\
                                    FROM {table}\
                                    WHERE {where} = ?", (meaning,))
        self.cur.execute(f"UPDATE {table} \
                           SET {key} = ? \
                           WHERE {where} = ?", (value + result.fetchone()[0], meaning))
        return self.conn.commit()

    def get_value(self, key: str, where: str, meaning: str, table: str = 'users'):

        result = self.cur.execute(f"SELECT {key} \
                                    FROM '{table}' \
                                    WHERE {where} = ?", (meaning,))
        return result.fetchone()[0]
    
    def update_value(self, key: str, where: str, meaning: str, table: str = 'users', value: str = ''):
        self.cur.execute(f'UPDATE {table} \
                           SET {key} = "{value}" \
                           WHERE {where} = ?', (meaning,))
        return self.conn.commit()

    def get_all_line_key(self, key: str, table: str = 'users', order: str = None, sort_by: str = 'DESC'):
        query = f"SELECT {key} \
                  FROM {table}"
        if order is not None:
            query += f" ORDER BY {order} {sort_by}"
        result = self.cur.execute(query).fetchall()
        keys_list = key.split(',')
        if len(keys_list) == 1:
            return list(map(lambda x: x[0], result))
        result_list = []
        for piece in result:
            piece_dict = {keys_list[ind].strip(): particle for ind,
                          particle in enumerate(piece)}
            result_list.append(piece_dict)
        return result_list

    def delete(self, where: str, meaning: str, table: str = 'users'):
        self.cur.execute(f'DELETE FROM {table} \
                           WHERE {where} = ?', (meaning,))
        return self.conn.commit()


    def create_new_connection(self):
        new_conn = sqlite3.connect(self.db_file)
        new_cur = new_conn.cursor()
        return new_conn, new_cur

    def close(self, conn):
        conn.close()


flow_db = BotDB("flow.db")
