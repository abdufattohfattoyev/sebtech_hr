import json
import logging
import os

from aiogram import Dispatcher, types

from data.config import ADMINS

VOICE_STORE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "handlers", "users", "voice_store.json"
)

START_KB = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton("📋 Ariza topshirish")]],
    resize_keyboard=True
)


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot faollashdi!")
        except Exception as err:
            logging.exception(err)

    await _broadcast_start_kb(dp)


async def _broadcast_start_kb(dp: Dispatcher):
    if not os.path.exists(VOICE_STORE_PATH):
        return
    try:
        with open(VOICE_STORE_PATH, "r") as f:
            store = json.load(f)
    except Exception:
        return

    user_ids = store.get("users", [])
    sent = 0
    for uid in user_ids:
        try:
            await dp.bot.send_message(
                uid,
                "🔄 Bot yangilandi! Ariza topshirish uchun quyidagi tugmani bosing.",
                reply_markup=START_KB
            )
            sent += 1
        except Exception:
            pass

    logging.info(f"Startup broadcast: {sent}/{len(user_ids)} foydalanuvchiga yuborildi.")
