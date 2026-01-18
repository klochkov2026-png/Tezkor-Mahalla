import asyncio
import sqlite3
import os
from os import getenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# TOKENNI XAVFSIZ O'QISH
TOKEN = getenv("BOT_TOKEN", "8513665563:AAHKtLubWM0UlWpDrpzf86scpGlksXuLLUQ")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Bazani tekshirish va jadval yaratish funksiyasi
def init_db():
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS hududlar 
               (id INTEGER PRIMARY KEY, viloyat TEXT, tuman TEXT, mahalla TEXT, 
                rais TEXT, rais_tel TEXT, inspektor TEXT, inspektor_tel TEXT, 
                yoshlar TEXT, yoshlar_tel TEXT, hokim_yord TEXT, hokim_yord_tel TEXT,
                xotin_qizlar TEXT, xotin_qizlar_tel TEXT,
                suv TEXT, gaz TEXT, t_hokimi TEXT, kadastr TEXT, iib TEXT, dxx TEXT)''')
        conn.commit()

def query_db(sql, params=()):
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    regions = query_db("SELECT DISTINCT viloyat FROM hududlar")
    
    # Agar baza bo'sh bo'lsa, foydalanuvchiga ogohlantirish
    if not regions:
        await message.answer("ℹ️ <b>Baza hozircha bo'sh.</b>\nIltimos, ma'lumotlarni yuklang.", parse_mode="HTML")
        return

    buttons = []
    for i in range(0, len(regions), 2):
        row = [InlineKeyboardButton(text=f"📍 {regions[i][0]}", callback_data=f"v_{regions[i][0]}")]
        if i + 1 < len(regions):
            row.append(InlineKeyboardButton(text=f"📍 {regions[i+1][0]}", callback_data=f"v_{regions[i+1][0]}"))
        buttons.append(row)
    
    text = (
        "<b>👋 Assalomu alaykum!</b>\n"
        "<b>🏙 TEZKOR MAHALLA tizimiga xush kelibsiz.</b>\n"
        "────────────────────\n"
        "⬇️ <b>Davom etish uchun viloyatni tanlang:</b>"
    )
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

# ... (qolgan callback_query kodlari avvalgidek qoladi)

async def main():
    init_db() # Bot boshlanishida bazani tekshiradi
    await dp.start_polling(bot)

if __name__ =="__main__":
    asyncio.run(main())
