import asyncio
import sqlite3
import os
from os import getenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = getenv("BOT_TOKEN", "8513665563:AAHKtLubWM0UlWpDrpzf86scpGlksXuLLUQ")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Baza jadvalini avtomatik yaratish (Agar u yo'q bo'lsa)
def init_db():
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS hududlar 
               (id INTEGER PRIMARY KEY, viloyat TEXT, tuman TEXT, mahalla TEXT, 
                rais TEXT, rais_tel TEXT, inspektor TEXT, inspektor_tel TEXT, 
                yoshlar TEXT, yoshlar_tel TEXT, hokim_yord TEXT, hokim_yord_tel TEXT,
                xotin_qizlar TEXT, xotin_qizlar_tel TEXT,
                suv TEXT, gaz TEXT, t_hokimi TEXT, kadastr TEXT, iib TEXT, dxx TEXT)''')
        # Agar baza bo'sh bo'lsa, namunaviy ma'lumot qo'shish (Sirdaryo misolida)
        cur.execute("SELECT COUNT(*) FROM hududlar")
        if cur.fetchone()[0] == 0:
            sample_data = ('Sirdaryo', 'Sardoba', "Do'stlik MFY", 'Eshmatov J.', '+998901234567', 'Aliyev B.', '+998911234567', 'Karimov Y.', '+998931234567', 'Sodiqov H.', '+998941234567', 'Umarova M.', '+998991234567', '1055', '1104', '76 221-12-12', '76 221-00-00', '102', '1008')
            cur.execute("INSERT INTO hududlar (viloyat, tuman, mahalla, rais, rais_tel, inspektor, inspektor_tel, yoshlar, yoshlar_tel, hokim_yord, hokim_yord_tel, xotin_qizlar, xotin_qizlar_tel, suv, gaz, t_hokimi, kadastr, iib, dxx) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", sample_data)
        conn.commit()

def query_db(sql, params=()):
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    regions = query_db("SELECT DISTINCT viloyat FROM hududlar")
    buttons = []
    for i in range(0, len(regions), 2):
        row = [InlineKeyboardButton(text=f"📍 {regions[i][0]}", callback_data=f"v_{regions[i][0]}")]
        if i + 1 < len(regions):
            row.append(InlineKeyboardButton(text=f"📍 {regions[i+1][0]}", callback_data=f"v_{regions[i+1][0]}"))
        buttons.append(row)
    
    text = (
        "<b>👋 Assalomu alaykum!</b>\n"
        "<b>🏙 TEZKOR MAHALLA TIZIMI</b>\n"
        "────────────────────\n"
        "<i>Mahallangiz mas'ullari bilan bog'lanish uchun hududni tanlang:</i>"
    )
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("v_"))
async def get_dist(callback: types.CallbackQuery):
    v_name = callback.data.split("_")[1]
    districts = query_db("SELECT DISTINCT tuman FROM hududlar WHERE viloyat=?", (v_name,))
    buttons = [[InlineKeyboardButton(text=f"🏙 {d[0]} tumani", callback_data=f"t_{v_name}_{d[0]}")] for d in districts]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")])
    await callback.message.edit_text(f"💎 <b>{v_name} viloyati</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("t_"))
async def get_mhl(callback: types.CallbackQuery):
    _, v, t = callback.data.split("_")
    mahallas = query_db("SELECT mahalla FROM hududlar WHERE viloyat=? AND tuman=?", (v, t))
    buttons = [[InlineKeyboardButton(text=f"🏘 {m[0]}", callback_data=f"m_{m[0]}")] for m in mahallas]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"v_{v}")])
    await callback.message.edit_text(f"📍 <b>{t} tumani</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("m_"))
async def show_final(callback: types.CallbackQuery):
    m_name = callback.data.split("_")[1]
    d = query_db("SELECT * FROM hududlar WHERE mahalla=?", (m_name,))[0]
    text = (
        f"🏘 <b>MAHALLA: {d[3].upper()}</b>\n"
        f"────────────────────\n"
        f"👤 <b>MAS'ULLAR:</b>\n"
        f"┣ <b>Rais:</b> {d[4]} 📞 <code>{d[5]}</code>\n"
        f"┣ <b>Inspektor:</b> {d[6]} 📞 <code>{d[7]}</code>\n"
        f"┣ <b>Yoshlar yetakchisi:</b> {d[8]} 📞 <code>{d[9]}</code>\n"
        f"┣ <b>Hokim yordamchisi:</b> {d[10]} 📞 <code>{d[11]}</code>\n"
        f"┗ <b>Ayollar faoli:</b> {d[12]} 📞 <code>{d[13]}</code>\n\n"
        f"⚡️ <b>XIZMATLAR:</b>\n"
        f"💧 <b>Suv:</b> <code>{d[14]}</code> | 🔥 <b>Gaz:</b> <code>{d[15]}</code>\n\n"
        f"🏢 <b>TUMAN:</b>\n"
        f"🏛 <b>Hokim:</b> {d[16]}\n"
        f"🚨 <b>IIB:</b> <code>{d[18]}</code> | 🛡 <b>DXX:</b> <code>{d[19]}</code>\n"
        f"────────────────────\n"
        f"👉 <i>Raqamni bosib nusxalashingiz mumkin.</i>"
    )
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Bosh menyu", callback_data="back")]]), parse_mode="HTML")

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await cmd_start(callback.message)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
