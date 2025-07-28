import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}
order_stats = {"total": 0, "done": 0, "pending": 0}


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer("👋 Привет! Введи свой username (например: @user123):")


@dp.message_handler(commands=['admin'])
async def admin_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        text = (f"📊 Статистика заказов:\n"
                f"Всего: {order_stats['total']}\n"
                f"✅ Выполнено: {order_stats['done']}\n"
                f"🕒 Ожидают: {order_stats['pending']}")
        await message.answer(text)


@dp.message_handler(lambda msg: msg.text.startswith("@"))
async def handle_username(message: types.Message):
    user_data[message.from_user.id] = message.text
    order_stats["total"] += 1
    order_stats["pending"] += 1
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("✅ Я оплатил")
    await message.answer("Спасибо! После оплаты нажми кнопку ниже 👇", reply_markup=keyboard)


@dp.message_handler(lambda msg: msg.text == "✅ Я оплатил")
async def confirm_payment(message: types.Message):
    username = user_data.get(message.from_user.id, "неизвестно")
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="✅ Подтвердить заказ",
        callback_data=f"confirm:{message.from_user.id}:{username}"
    )
    keyboard.add(button)
    await bot.send_message(ADMIN_ID, f"💸 Новый заказ от @{message.from_user.username}\n"
                                     f"Username: {username}", reply_markup=keyboard)
    await message.answer("⏳ Ожидается подтверждение администратора...")


@dp.callback_query_handler(lambda c: c.data.startswith("confirm:"))
async def handle_confirm(callback: types.CallbackQuery):
    _, user_id, username = callback.data.split(":")
    user_id = int(user_id)
    order_stats["done"] += 1
    order_stats["pending"] -= 1
    await bot.send_message(user_id, f"✅ Ваш заказ выполнен! Звёзды отправлены на {username}.")
    await callback.answer("Заказ подтвержден ✅")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
