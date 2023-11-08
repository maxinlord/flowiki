import datetime
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


def get_message_text(unique_name, d=None) -> str:
    if d is None:
        d = {}
    mode = flow_db.get(
        key="box",
        where="name",
        meaning="program_mode_for_text",
        table="values",
    )
    try:
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="message_texts"
        )
    except Exception:
        flow_db.add_new_message_text(name=unique_name)
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="message_texts"
        )
    text_true = text.format(**d)
    return f"[{unique_name}]\n{text_true}" if mode == "on" else text_true


def get_button_text(unique_name, d=None) -> str:
    if d is None:
        d = {}
    mode = flow_db.get(
        key="box",
        where="name",
        meaning="program_mode_for_text",
        table="values",
    )
    try:
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="button_texts"
        )
    except Exception:
        flow_db.add_new_button_text(name=unique_name)
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="button_texts"
        )
    text_true = text.format(**d)
    return f"[{unique_name}]\n{text_true}" if mode == "on" else text_true


def update_dict_users(name: str, dict_users: list) -> list:
    for num, i in enumerate(dict_users):
        if i["name"] == name:
            dict_users[num]["select"] = not dict_users[num]["select"]
    return dict_users

def count_page(size_one_page, quantity_users) -> int:
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
    return file_name.split('.')[1] == 'xlsx'

def get_table_name():
    table_names = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", flow_db.conn)
    return table_names