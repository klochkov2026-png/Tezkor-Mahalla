import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8513665563:AAHKtLubWM0UlWpDrpzf86scpGlksXuLLUQ"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def query_db(sql, params=()):
    with sqlite3.connect('mahalla_bazasi.db') as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Viloyatlar ro'yxati
    v_list = ["Sirdaryo", "Toshkent sh.", "Samarqand", "Andijon", "Farg'ona", "Namangan", "Buxoro", "Navoiy", "Qashqadaryo", "Surxondaryo", "Xorazm", "Jizzax"]
    buttons = []
    for i in range(0, len(v_list), 2):
        row = [InlineKeyboardButton(text=v_list[i], callback_data=f"v_{v_list[i]}")]
        if i + 1 < len(v_list):
            row.append(InlineKeyboardButton(text=v_list[i+1], callback_data=f"v_{v_list[i+1]}"))
        buttons.append(row)
    
    await message.answer("<b>🏙 TEZKOR MAHALLA TIZIMI</b>\n\nDavom etish uchun viloyatni tanlang:", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("v_"))
async def get_dist(callback: types.CallbackQuery):
    v_name = callback.data.split("_")[1]
    districts = query_db("SELECT DISTINCT tuman FROM hududlar WHERE viloyat=?", (v_name,))
    if not districts:
        await callback.answer("Hozircha ma'lumot yo'q", show_alert=True)
        return
    buttons = [[InlineKeyboardButton(text=d[0], callback_data=f"t_{v_name}_{d[0]}")] for d in districts]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")])
    await callback.message.edit_text(f"📍 <b>{v_name}</b>\nTumanni tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("t_"))
async def get_mhl(callback: types.CallbackQuery):
    _, v, t = callback.data.split("_")
    mahallas = query_db("SELECT mahalla FROM hududlar WHERE viloyat=? AND tuman=?", (v, t))
    buttons = [[InlineKeyboardButton(text=m[0], callback_data=f"m_{m[0]}")] for m in mahallas]
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"v_{v}")])
    await callback.message.edit_text(f"📍 <b>{t} tumani</b>\nMahallani tanlang:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("m_"))
async def show_all(callback: types.CallbackQuery):
    m_name = callback.data.split("_")[1]
    d = query_db("SELECT * FROM hududlar WHERE mahalla=?", (m_name,))[0]
    
    text = (
        f"🏘 <b>{d[3].upper()}</b>\n"
        f"<i>Sirdaryo viloyati, Sardoba tumani</i>\n\n"
        f"📌 <b>MAHALLA MAS'ULLARI:</b>\n"
        f"👤 <b>Rais:</b> {d[4]} (<code>{d[5]}</code>)\n"
        f"👮‍♂️ <b>Inspektor:</b> {d[6]} (<code>{d[7]}</code>)\n"
        f"👦 <b>Yoshlar yetakchisi:</b> {d[8]} (<code>{d[9]}</code>)\n"
        f"💼 <b>Hokim yordamchisi:</b> {d[10]} (<code>{d[11]}</code>)\n"
        f"👩 <b>Xotin-qizlar faoli:</b> {d[12]} (<code>{d[13]}</code>)\n\n"
        f"📌 <b>XIZMATLAR:</b>\n"
        f"💧 <b>Suv:</b> <code>{d[14]}</code> | 🔥 <b>Gaz:</b> <code>{d[15]}</code>\n\n"
        f"📌 <b>TUMAN VA TEZKOR:</b>\n"
        f"🏛 <b>Hokim:</b> {d[16]}\n"
        f"🗺 <b>Kadastr:</b> {d[17]}\n"
        f"🚨 <b>IIB:</b> <code>{d[18]}</code> | 🛡 <b>DXX:</b> <code>{d[19]}</code>\n\n"
        f"ℹ️ <i>Raqam ustiga bossangiz, nusxalanadi!</i>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Bosh menyu", callback_data="back")]])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "back")
async def back(callback: types.CallbackQuery):
    await cmd_start(callback.message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
