import sqlite3


def to_str_objects(data: list):
    return [str(x) for x in data]


def is_float(num: str) -> bool:
    if num.isdigit():
        return False
    try:
        float(num)
        return True
    except Exception:
        return False


class BotDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def user_exists(self, id_user):
        result = self.cur.execute(
            "SELECT `id` \
                                  FROM `users` \
                                  WHERE `id` = ?",
            (id_user,),
        )
        return bool(len(result.fetchall()))

    def rule_exists(self, id_user):
        result = self.cur.execute(
            "SELECT `rule` \
                                  FROM `users` \
                                  WHERE `id` = ?",
            (id_user,),
        )
        return result.fetchone()[0] != None

    def add_new_text(self, name: str):
        self.cur.execute(
            "INSERT INTO `message_texts` \
                         (`name`) VALUES (?)",
            (name,),
        )
        return self.conn.commit()

    def add_new_reason(
        self, id_user: str, reason: str, id_owner_reason: str, date: str, num
    ):
        self.cur.execute(
            "INSERT INTO `history_reasons` (id, reason, owner_reason, date, num) VALUES (?, ?, ?, ?, ?)",
            (id_user, reason, id_owner_reason, date, num),
        )
        return self.conn.commit()

    def add_new_button(self, name: str):
        self.cur.execute(
            "INSERT INTO `button_texts` \
                         (`name`) VALUES (?)",
            (name,),
        )
        return self.conn.commit()

    def add_user(self, id_user):  # Добавляем юзера в базу
        self.cur.execute(
            "INSERT INTO `users` \
                         (`id`) VALUES (?)",
            (id_user,),
        )
        return self.conn.commit()

    def add_value(
        self, key: str, where: str, meaning: str, table: str = "users", value: str = 0
    ):
        result = self.cur.execute(
            f"SELECT {key}\
                                    FROM {table}\
                                    WHERE {where} = ?",
            (meaning,),
        )
        self.cur.execute(
            f"UPDATE {table} \
                           SET {key} = ? \
                           WHERE {where} = ?",
            (value + result.fetchone()[0], meaning),
        )
        return self.conn.commit()

    def get_value(self, key: str, where: str, meaning: str, table: str = "users"):
        result = self.cur.execute(
            f"SELECT {key} \
                                    FROM '{table}' \
                                    WHERE {where} = ?",
            (meaning,),
        )
        return result.fetchone()[0]

    def update_value(
        self, key: str, where: str, meaning: str, table: str = "users", value: str = ""
    ):
        self.cur.execute(
            f'UPDATE {table} \
                           SET {key} = "{value}" \
                           WHERE {where} = ?',
            (meaning,),
        )
        return self.conn.commit()

    def get_all_line_key(
        self, key: str, table: str = "users", order: str = None, sort_by: str = "DESC"
    ):
        query = f"SELECT {key} \
                  FROM {table}"
        if order is not None:
            query += f" ORDER BY {order} {sort_by}"
        result = self.cur.execute(query).fetchall()
        keys_list = key.split(",")
        if len(keys_list) == 1:
            return list(map(lambda x: x[0], result))
        result_list = []
        for piece in result:
            piece_dict = {
                keys_list[ind].strip(): particle for ind, particle in enumerate(piece)
            }
            result_list.append(piece_dict)
        return result_list

    def get_ids_admin(self):
        query = "SELECT id FROM users WHERE rule = 'admin'"
        result = self.cur.execute(query).fetchall()
        return [i[0] for i in result]

    def delete(self, where: str, meaning: str, table: str = "users"):
        self.cur.execute(
            f"DELETE FROM {table} \
                           WHERE {where} = ?",
            (meaning,),
        )
        return self.conn.commit()

    def add_2dd(
        self, table: str, key: str, where: str, meaning: str, throw_data: list = None
    ):
        if throw_data is None:
            throw_data = []
        existing_data = self.get_value(
            key=key, where=where, meaning=meaning, table=table
        ).strip(",")
        new_data = "," + ":".join(to_str_objects(throw_data))
        data = existing_data + new_data
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, value=data
        )

    def parse_2dd(self, table: str, key: str, where: str, meaning: str):
        existing_data = self.get_value(
            key=key, where=where, meaning=meaning, table=table
        ).strip(",")
        list_existing_data = existing_data.split(",")
        headers = list_existing_data.pop(0).split(":")
        small_data, data = {}, []
        for piece in list_existing_data:
            for ind, particle in enumerate(piece.split(":")):
                if particle.isdigit() or is_float(particle):
                    particle = float(particle) if is_float(particle) else int(particle)
                small_data[headers[ind]] = particle
            data.append(small_data)
            small_data = {}
        return data

    def get_2dd(
        self,
        table: str,
        key: str,
        where: str,
        meaning: str,
        where_data: str = "id",
        get_data: str = "id",
        meaning_data: str = "0",
    ):
        try:
            data = self.parse_2dd(key=key, where=where, meaning=meaning, table=table)
        except Exception as e:
            return e
        for piece in data:
            if str(piece[where_data]) == meaning_data:
                return piece[get_data]

    def increase_value_2dd(
        self,
        table: str,
        key: str,
        where: str,
        meaning: str,
        add: str,
        where_data: str = "id",
        add_data: str = "id",
        sign_after_comma: int = 2,
        meaning_data: str = "0",
    ):
        try:
            data = self.parse_2dd(key=key, where=where, meaning=meaning, table=table)
            ind_where = data[0].index(where_data)
            ind_add = data[0].index(add_data)
        except Exception as e:
            return e
        headers = ":".join(data[0])
        for piece in data[1:]:
            if str(piece[ind_where]) == meaning_data:
                piece[ind_add] = (
                    round(piece[ind_add] + add, sign_after_comma)
                    if is_float(str(piece[ind_add]))
                    else piece[ind_add] + add
                )
            headers += "," + ":".join(to_str_objects(piece))
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, value=headers.strip(",")
        )

    def delete_2dd(
        self, table: str, key: str, where: str, meaning: str, unique_value_data: str
    ):
        data = self.get_value(key=key, where=where, meaning=meaning, table=table).strip(
            ","
        )
        list_data = data.split(",")
        headers = list_data[0]
        new_data = "".join(
            f",{piece}" for piece in list_data[1:] if unique_value_data not in piece
        )
        data = headers + new_data
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, value=data.strip(",")
        )

    def update_value_2dd(
        self,
        table: str,
        key: str,
        where: str,
        meaning: str,
        value: str,
        where_data: str = "id",
        meaning_data: str = "0",
        update_data: str = "id",
    ):
        try:
            data: list = self.parse_2dd(
                key=key, where=where, meaning=meaning, table=table
            )
        except Exception as e:
            return print(e)
        headers = ":".join(data[0].keys())
        for piece in data:
            piece: dict
            if str(piece[where_data]) == meaning_data:
                piece[update_data] = value
            headers += "," + ":".join(to_str_objects(piece.values()))
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, value=headers.strip(",")
        )

    def add_header_2dd(
        self,
        table: str,
        key: str,
        where: str,
        meaning: str,
        name_new_header: str,
        default_value: str,
    ):
        data = self.get_value(key=key, where=where, meaning=meaning, table=table).strip(
            ","
        )
        list_data = data.split(",")
        list_new_data = [f"{list_data[0]}:{name_new_header}"]
        list_new_data.extend(f"{piece}:{default_value}" for piece in list_data[1:])
        data = ",".join(list_new_data)
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, text=data.strip(",")
        )

    def delete_header_2dd(
        self, table: str, key: str, where: str, meaning: str, name_header: str
    ):
        try:
            data = self.get_value(
                key=key, where=where, meaning=meaning, table=table
            ).strip(",")
            list_data = data.split(",")
            ind_header = list_data[0].split(":").index(name_header)
        except Exception as e:
            return e
        list_headers = list_data[0].split(":")
        list_headers.pop(ind_header)
        list_new_data = [":".join(list_headers)]
        for piece in list_data[1:]:
            piece = piece.split(":")
            piece.pop(ind_header)
            piece = ":".join(piece)
            list_new_data.append(piece)
        data = ",".join(list_new_data)
        self.update_value(
            key=key, where=where, meaning=meaning, table=table, value=data.strip(",")
        )

    def create_new_connection(self):
        new_conn = sqlite3.connect(self.db_file)
        new_cur = new_conn.cursor()
        return new_conn, new_cur

    def close(self, conn):
        conn.close()
