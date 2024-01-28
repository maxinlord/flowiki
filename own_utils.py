import datetime
import random
import string
from typing import List
from init_db import flow_db
import pandas as pd
import re
import datetime
import emoji

weekday_tr = {
    "monday": "Понедельник",
    "tuesday": "Вторник",
    "wednesday": "Среда",
    "thursday": "Четверг",
    "friday": "Пятница",
    "saturday": "Суббота",
    "sunday": "Воскресенье",
}


def get_current_date(format="%Y-%m-%d"):
    """
    Возвращает текущую дату в указанном формате.

    Параметры:
    format (строка): Формат даты (по умолчанию "%Y-%m-%d").

    Возвращает:
    строка: Текущая дата в указанном формате.
    """
    current_date = datetime.datetime.now()
    return current_date.strftime(format)


def get_button(name: str, throw_data: dict = None) -> str:
    text_mode = flow_db.get_value(
        key="box", where="name", meaning="program_mode_for_text", table="values"
    )
    try:
        text = flow_db.get_value(
            key="text", where="name", meaning=name, table="button_texts"
        )
    except Exception:
        flow_db.add_new_button(name)
        text = "created now"
    text = text.format(**throw_data) if throw_data else text
    return f"({name})\n\n{text}" if text_mode == "on" else text


def get_text(name: str, throw_data: dict = None) -> str:
    text_mode = flow_db.get_value(
        key="box",
        where="name",
        meaning="program_mode_for_text",
        table="values",
    )
    try:
        text = flow_db.get_value(
            key="text", where="name", meaning=name, table="message_texts"
        )
    except Exception:
        flow_db.add_new_text(name=name)
        text = "created now"
    text = text.format(**throw_data) if throw_data else text
    return f"({name})\n\n{text}" if text_mode == "on" else text


def update_dict_users(id_user: str, dict_users: list) -> list:
    for num, i in enumerate(dict_users):
        if i["id"] == id_user:
            dict_users[num]["select"] = not dict_users[num]["select"]
    return dict_users


def count_page(size_one_page, quantity_users) -> int:
    if quantity_users % size_one_page == 0:
        return quantity_users / size_one_page
    return (quantity_users // size_one_page) + 1


def get_xlsx_table(conn, table_name):
    # Write each table to a separate worksheet in the Excel file
    with pd.ExcelWriter(f"{table_name}.xlsx") as writer:
        df = pd.read_sql(f"SELECT * FROM '{table_name}'", conn)
        df.to_excel(writer, sheet_name=table_name, index=False)


def write_excel_to_db(excel_file, conn):
    # Read the data from the Excel file
    with pd.ExcelFile(excel_file) as xlsx:
        sheets = xlsx.sheet_names
        dfs = {sheet: xlsx.parse(sheet) for sheet in sheets}

    # Write each worksheet in the Excel file to a separate table in the database
    for sheet_name, df in dfs.items():
        df.to_sql(sheet_name, conn, if_exists="replace", index=False)


def is_xlsx_extend(file_name: str):
    return file_name.split(".")[1] == "xlsx"


def get_table_name():
    table_names = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table'", flow_db.conn
    )
    return table_names


def get_dict_users():
    l_users = flow_db.get_all_line_key(
        key="rule, fio, id, balance_flow", order="fio", sort_by="ASC"
    )
    d_users = [
        {
            "name": i["fio"],
            "balance_flow": i["balance_flow"],
            "select": False,
            "id": i["id"],
            "rule": i["rule"],
        }
        for i in l_users
    ]
    return d_users


def wrap(
    num: int,
    q_signs_after_comma: int = 2,
    is_persent: bool = False,
    format: str = "code",
    add_sign: str = "",
) -> str:
    if is_persent:
        add_sign = "%"
        num *= 100
    num = round(num, q_signs_after_comma)
    if float(num) % 1 != 0:
        return "<{format}>{:,.{}f}</{format}>{add_sign}".format(
            float(num), q_signs_after_comma, format=format, add_sign=add_sign
        )
    return "<{format}>{:,}</{format}>{add_sign}".format(
        int(num), format=format, add_sign=add_sign
    )


def create_custom_id(len_tag: int = 8):
    signs = string.digits + string.ascii_letters
    tag = "".join(random.choices(signs, k=len_tag))
    return f"custom:{tag}"


def view_selected_users(d_users: dict):
    if l_user := [user["fio"] for user in d_users if user["select"]]:
        last = l_user.pop(-1)
        if l_user:
            return "\n     ├" + "\n     ├".join(l_user).strip(",") + f"\n     └{last}"
        return f"\n     └{last}"
    return get_text("no_choise_users")


def count_index_for_page(page_num, size_one_page):
    start = size_one_page * (page_num - 1)
    end = start + size_one_page
    return int(start), int(end)


def create_text_historys(raw_data, page_num):
    lenght_d = len(raw_data)
    start, end = count_index_for_page(page_num, 5)
    end = min(end, lenght_d)
    historys = [
        get_text(
            "pattern_line_history_transfer",
            throw_data={
                "date": raw_data[i]["date"],
                "num": raw_data[i]["num"],
                "reason": raw_data[i]["reason"],
                "owner_reason": flow_db.get_value(
                    key="fio", where="id", meaning=raw_data[i]["owner_reason"]
                ),
            },
        )
        for i in range(start, end)
    ]
    return "\n".join(historys)


def de_active_presets(user_presets):
    for preset in user_presets:
        preset["is_active"] = 0
    return user_presets


def activate_preset(user_presets, id_preset):
    for preset in user_presets:
        if preset["id_preset"] == id_preset:
            preset["is_active"] = 1
    return user_presets


def delete_preset(user_presets, id_preset):
    return [preset for preset in user_presets if preset["id_preset"] != id_preset]


def delete_notification(user_notifications, id_notify):
    return [notify for notify in user_notifications if notify["id_notify"] != id_notify]


weekday = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}


def extract_date(text: str):  # sourcery skip: use-named-expression
    date_regex = r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    match = re.search(date_regex, text)
    if match:
        date_str = match.group()
        date = datetime.datetime.strptime(date_str, "%d.%m.%Y")
        key_weekday = date.weekday()
        return date.strftime("%d.%m.%Y"), weekday[key_weekday]
    return ""

# print(extract_date('hfgf') or "rtrtr")


def extract_time(text: str) -> str:  # sourcery skip: use-named-expression
    time_regex = r"\d{1,2}:\d{1,2}"
    match_time = re.search(time_regex, text)
    if match_time:
        time_str = match_time.group()
        date_time = datetime.datetime.strptime(time_str, "%H:%M")
        return date_time.strftime("%H:%M")
    return ""


def is_date_today(str_date: str):
    return (
        datetime.datetime.strptime(str_date, "%d.%m.%Y").date()
        == datetime.datetime.today().date()
    )


async def clean_notification(id_user):
    notifications = flow_db.parse_2dd(
        table="users", key="notifications", where="id", meaning=id_user
    )
    for notify in notifications:
        if notify["is_active"] == 0:
            flow_db.delete_2dd(
                table="users",
                key="notifications",
                where="id",
                meaning=int(id_user),
                unique_value_data="0",
            )


def set_preset(id_user, id_preset_to_activate):
    # sourcery skip: use-named-expression
    presets = flow_db.parse_2dd(
        table="users", key="presets", where="id", meaning=id_user
    )

    if not presets:
        return
    id_old_preset = [
        preset["id_preset"] for preset in presets if preset["is_active"] == 1
    ]
    if id_old_preset:
        flow_db.update_value_2dd(
            table="users",
            key="presets",
            where="id",
            meaning=id_user,
            where_data="id_preset",
            meaning_data=id_old_preset[0],
            update_data="is_active",
            value=0,
        )
    if id_preset_to_activate == "base_preset":
        return
    try:
        flow_db.update_value_2dd(
            table="users",
            key="presets",
            where="id",
            meaning=id_user,
            where_data="id_preset",
            meaning_data=id_preset_to_activate,
            update_data="is_active",
            value=1,
        )
    except:
        pass


def get_all_reason():
    data = flow_db.get_all_line_key(
        table="history_reasons", key="tag, id, reason, date, num, message_id"
    )[::-1]
    update_data = []
    for reason in data:
        reason["name"] = flow_db.get_value(
            key="fio", where="id", meaning=reason["id"]
        ).split(" ")[0]
        reason["is_choose"] = False
        update_data.append(reason)
    return update_data


def get_all_users_visit():
    users = flow_db.get_all_line_key(key="id, rule, fio")
    users = [user for user in users if user["rule"] == "user"]
    text = "\n".join(
        get_text(
            "patter_line_stat_visit",
            throw_data={
                "quantity_visit": flow_db.get_num_of_visits_user(user["id"]),
                "fio": user["fio"],
            },
        )
        for user in users
    )
    return text


def update_dict_reasons(tag_reason: str, dict_reasons: list) -> list:
    for num, i in enumerate(dict_reasons):
        if i["tag"] == tag_reason:
            dict_reasons[num]["is_choose"] = not dict_reasons[num]["is_choose"]
    return dict_reasons


def delete_choose_reasons(reasons: list):
    for reason in reasons:
        flow_db.delete(table="history_reasons", where="tag", meaning=reason["tag"])
        flow_db.add_value(
            key="balance_flow", where="id", meaning=reason["id"], value=-reason["num"]
        )


import unicodedata


def is_human_emoji(emoji_str):
    # Итерируем по каждому символу в строке эмодзи
    for char in emoji_str:
        # Проверяем, принадлежит ли категория символа к "Человеку" в Unicode

        to_ban = [
            "MAN",
            "WOMAN",
            "ADULT",
            "PERSON",
            "FEMALE",
            "MALE",
            "BABY",
            "GIRL",
            "BOY",
            "PALM",
        ]
        for i in to_ban:
            if i in unicodedata.name(char, "").upper():
                return True
        print(unicodedata.name(char, "").upper())
    return False


# Пример использования


# data = get_data_users()
# print(filter_(data, rule="user"))
