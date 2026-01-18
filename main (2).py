import asyncio
import sqlite3
import os
from os import getenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# TOKENNI XAVFSIZ O'QISH
# Render dagi Environment Variables bo'limiga ushbu tokenni BOT_TOKEN nomi bilan qo'shgan bo'lishingiz kerak
TOKEN = getenv("BOT_TOKEN", "8513665563:AAHKtLubWM0UlWpDrpzf86scpGlksXuLLUQ")
bot = Bot(token=TOKEN)
dp = Dispatcher()

def query_db(sql, params=()):
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    regions = query_db("SELECT DISTINCT viloyat FROM hududlar")
    buttons = []
    # Tugmalarni chiroyli 2 qatorda terish
    for i in range(0, len(regions), 2):
        row = [InlineKeyboardButton(text=f"📍 {regions[i][0]}", callback_data=f"v_{regions[i][0]}")]
        if i + 1 < len(regions):
            row.append(InlineKeyboardButton(text=f"📍 {regions[i+1][0]}", callback_data=f"v_{regions[i+1][0]}"))
        buttons.append(row)
    
    text = (
        "<b>👋 Assalomu alaykum!</b>\n"
        "<b>🏙 TEZKOR MAHALLA axborot tizimi</b>\n"
        "────────────────────\n"
        "<i>Ushbu bot orqali mahallangizdagi barcha mas'ul xodimlar bilan tezkor bog'lanishingiz mumkin.</i>\n\n"
        "⬇️ <b>Davom etish uchun viloyatni tanlang:</b>"
    )
    await message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("v_"))
async def get_dist(callback: types.CallbackQuery):
    v_name = callback.data.split("_")[1]
    districts = query_db("SELECT DISTINCT tuman FROM hududlar WHERE viloyat=? AND tuman IS NOT NULL", (v_name,))
    
    if not districts:
        await callback.answer("⚠️ Ushbu hudud bo'yicha ma'lumotlar tez orada yuklanadi!", show_alert=True)
        return

    buttons = [[InlineKeyboardButton(text=f"🏙 {d[0]} tumani", callback_data=f"t_{v_name}_{d[0]}")] for d in districts]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")])
    
    await callback.message.edit_text(f"💎 <b>{v_name} viloyati</b>\n\nKerakli tumanni tanlang:", 
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("t_"))
async def get_mhl(callback: types.CallbackQuery):
    _, v, t = callback.data.split("_")
    mahallas = query_db("SELECT mahalla FROM hududlar WHERE viloyat=? AND tuman=?", (v, t))
    buttons = [[InlineKeyboardButton(text=f"🏘 {m[0]}", callback_data=f"m_{m[0]}")] for m in mahallas]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"v_{v}")])
    await callback.message.edit_text(f"📍 <b>{t} tumani</b>\nMahallani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("m_"))
async def show_final(callback: types.CallbackQuery):
    m_name = callback.data.split("_")[1]
    res = query_db("SELECT * FROM hududlar WHERE mahalla=?", (m_name,))
    if not res: return
    d = res[0]
    
    text = (
        f"🏘 <b>MAHALLA: {d[3].upper()}</b>\n"
        f"📌 <i>{d[2]} tumani, {d[1]}</i>\n"
        f"────────────────────\n"
        f"👤 <b>MAHALLA MAS'ULLARI:</b>\n"
        f"┣ <b>Rais:</b> {d[4]} 📞 <code>{d[5]}</code>\n"
        f"┣ <b>Inspektor:</b> {d[6]} 📞 <code>{d[7]}</code>\n"
        f"┣ <b>Yoshlar yetakchisi:</b> {d[8]} 📞 <code>{d[9]}</code>\n"
        f"┣ <b>Hokim yordamchisi:</b> {d[10]} 📞 <code>{d[11]}</code>\n"
        f"┗ <b>Ayollar faoli:</b> {d[12]} 📞 <code>{d[13]}</code>\n\n"
        f"🔌 <b>KOMMUNAL XIZMATLAR:</b>\n"
        f"┣ 💧 <b>Suv:</b> <code>{d[14]}</code>\n"
        f"┗ 🔥 <b>Gaz:</b> <code>{d[15]}</code>\n\n"
        f"🏛 <b>TUMAN BOSHQARMASI:</b>\n"
        f"┣ 🏦 <b>Hokim:</b> {d[16]}\n"
        f"┣ 🗺 <b>Kadastr:</b> {d[17]}\n"
        f"┣ 🚨 <b>IIB Tezkor:</b> <code>{d[18]}</code>\n"
        f"┗ 🛡 <b>DXX Tezkor:</b> <code>{d[19]}</code>\n"
        f"────────────────────\n"
        f"👉 <i>Raqam ustiga bossangiz nusxalanadi!</i>"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Bosh menyu", callback_data="back")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "back")
async def go_back(callback: types.CallbackQuery):
    await cmd_start(callback.message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
