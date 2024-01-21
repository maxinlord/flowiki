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
    menu_for_delete_history_reason,
    stat_onlines,
    shop_items,
    statistics, 
    user_mailing,
    set_emoji,
    any_message,
)
from own_utils import clean_notification, is_date_today, set_preset
import datetime

from tool_classes import User


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


async def notify_admin_remind(id_user, message, id_preset_to_activate):
    message = str(message)
    await bot.send_message(chat_id=id_user, text=message)
    User(id_user).preset.current_active_preset = id_preset_to_activate

async def notify_admin_once(id_user, message, id_preset_to_activate, job):
    message = str(message)
    await bot.send_message(chat_id=id_user, text=message)
    User(id_user).preset.current_active_preset = id_preset_to_activate
    notify = User(id_user).notification
    del notify[job]
    aioschedule.jobs.remove(d[job])


# async def job_sec():
#     print("hi")


async def job_minute():
    date = time.strftime("%X").split(":")
    if date[2] != "59":
        return
    for id_ in User(id_user=None):
        for notify in User(id_user=id_).notification:
            if notify["is_active"] == 0:
                job = d.get(notify["id_notify"])
                if job:
                    aioschedule.jobs.remove(job)
                    d.pop(notify["id_notify"])
                continue
            if d.get(notify["id_notify"]):
                continue
            if notify["type_notify"] == "once":
                date, time_ = notify['time'].split(' ')
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
                job = func_days[notify["weekday"]](notify["time"]).do(
                    notify_admin_remind,
                    id_user=id_,
                    message=notify["message"],
                    id_preset_to_activate=notify["id_preset"],
                )
                d[notify["id_notify"]] = job


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
