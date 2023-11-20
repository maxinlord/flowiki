import datetime
import random
import string
from typing import List
from db_func import flow_db
import pandas as pd


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
    except:
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
    except:
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
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
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


def get_data_users():
    l_users = flow_db.get_all_line_key(
        key="rule, fio, id, balance_flow", order="fio", sort_by="ASC"
    )
    d_users = [
        {
            "name": i["fio"],
            "balance": i["balance_flow"],
            "select": False,
            "id": i["id"],
            "rule": i["rule"],
        }
        for i in l_users
    ]
    d_users = filter_(d_users, rule="user")
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
    tag = ""
    signs = string.digits + string.ascii_letters
    for _ in range(len_tag):
        sign = random.choice(signs)
        tag += sign
    return f"custom:{tag}"


def filter_(data, **kwargs):
    """
    Filters a list of dictionaries based on specified conditions.

    Args:
        list_of_dicts (list[dict]): List of dictionaries to filter.
        **kwargs: Keyword arguments representing filter conditions.

    Returns:
        list[dict]: Filtered list of dictionaries.
    """
    return [
        d
        for d in data
        if all(
            k in d
            and (
                isinstance(v, str)
                and v in d[k]
                or isinstance(v, (int, float))
                and eval(f"{d[k]} {v}")
            )
            for k, v in kwargs.items()
        )
    ]


def view_selected_users(d_users: dict):
    l_user = []
    for user in d_users:
        if user["select"]:
            l_user.append(user["name"])

    if l_user:
        last = l_user.pop(-1)
        if l_user:
            return "\n     ├" + "\n     ├".join(l_user).strip(",") + f"\n     └{last}"
        return f"\n     └{last}"
    return "Не указано"


# data = get_data_users()
# print(filter_(data, rule="user"))
