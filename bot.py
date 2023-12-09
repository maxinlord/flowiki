import asyncio
import logging
from pprint import pprint
import sys
import time
from aiogram import Dispatcher
import aioschedule

from dispatcher import dp, bot
from init_db import flow_db
from handlers import (
    balance,
    flownomika,
    get_file,
    hand_reg,
    history_transfer,
    photo,
    start,
    top,
    options_for_admin,
    presets,
    view_options,
    notification,
    any_message,
)
from own_utils import clean_notification, is_date_today, set_preset, unwrap_2dd
import datetime

# Установка часового пояса на Московское время

d = {}
func_days = {
    "monday": aioschedule.every().monday.at,
    "tuesday": aioschedule.every().tuesday.at,
    "wednesday": aioschedule.every().wednesday.at,
    "thursday": aioschedule.every().thursday.at,
    "friday": aioschedule.every().friday.at,
    "saturday": aioschedule.every().saturday.at,
    "sunday": aioschedule.every().sunday.at,
}


async def notify_admin(id_user, message, id_preset_to_activate):
    await clean_notification(id_user)
    await bot.send_message(chat_id=id_user, text=str(message))
    set_preset(id_user, id_preset_to_activate)

async def notify_admin_once(id_user, message, id_preset_to_activate, job):
    await clean_notification(id_user)
    await bot.send_message(chat_id=id_user, text=str(message))
    set_preset(id_user, id_preset_to_activate)
    flow_db.delete_2dd(table='users', key='notifications', where='id', meaning=id_user, unique_value_data=job)
    aioschedule.jobs.remove(d[job])


async def job_sec():
    print("hi")


async def job_minute():
    date = time.strftime("%X").split(":")
    if date[2] != "59":
        return
    ids_admin = flow_db.get_ids_admin()
    for id_ in ids_admin:
        notifications = flow_db.parse_2dd(
            table="users", key="notifications", where="id", meaning=id_
        )
        for notify in notifications:
            if notify["is_active"] == 0:
                job = d.get(notify["id_notify"])
                if job:
                    aioschedule.jobs.remove(job)
                    d.pop(notify["id_notify"])
                continue
            if d.get(notify["id_notify"]):
                continue
            if notify["type_notify"] == "once":
                date, time_ = unwrap_2dd(notify['time']).split(' ')
                if is_date_today(date):
                    job = func_days[notify["weekday"]](time_).do(
                        notify_admin_once,
                        id_user=id_,
                        message=notify["message"],
                        id_preset_to_activate=notify["id_preset"],
                        job=notify["id_notify"]
                    )
                    d[notify["id_notify"]] = job
            if notify["type_notify"] == "remind":
                job = func_days[notify["weekday"]](unwrap_2dd(notify["time"])).do(
                    notify_admin,
                    id_user=id_,
                    message=notify["message"],
                    id_preset_to_activate=notify["id_preset"],
                )
                d[notify["id_notify"]] = job
    print(aioschedule.jobs)

async def job_hour():
    pass


# async def notify_admin():
#     await bot.send_message('', 'Notify you')
async def job():
    pass


async def scheduler():
    # aioschedule.every(1).seconds.do(job_sec)
    aioschedule.time.time
    aioschedule.every(1).seconds.do(job_minute)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, stream=sys.stdout)
    asyncio.run(main())
