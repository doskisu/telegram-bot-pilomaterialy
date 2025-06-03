import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram. types import CallbackQuery

# Логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения
API_TOKEN = os.getenv('BOT_TOKEN')
MANAGER_TELEGRAM_ID = 'raszd189'  # Telegram-никнейм менеджера (без @)

# Инициализируем бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Кнопка "Запрос фото"
def create_photo_request_button():
    button = [[InlineKeyboardButton(text="📷 Запросить фото", callback_data="request_photo")]]
    return InlineKeyboardMarkup(inline_keyboard=button)

# Кнопки связи с менеджером
def create_contact_buttons():
    buttons = [
        [InlineKeyboardButton(text="📞 Позвонить менеджеру", url="tg://call?phone_number=+79917870066")],
        [InlineKeyboardButton(text="💬 Написать менеджеру", url=f"https://t.me/{MANAGER_TELEGRAM_ID}")] 
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons) 
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для заказа пиломатериалов. Напишите, например: "
        "'Минимальный объем заказа', 'Сорта пиломатериалов' или нажмите кнопку ниже.",
        reply_markup=create_photo_request_button()
    )

# Обработчик нажатий на кнопки
@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery):
    if callback_query.data == "request_photo":
        # Отправляем клиенту инструкцию
        await callback_query.message.edit_text(
            "Чтобы получить фотографии продукции, напишите нашему менеджеру.",
            reply_markup=create_contact_buttons()
        )
        
        # Отправляем уведомление менеджеру
        user = callback_query.from_user
        user_info = f"[{user.id}](tg://user?id={user.id})"
        await bot.send_message(
            MANAGER_TELEGRAM_ID,
            f"{user_info} хочет получить фотографии продукции.",
            parse_mode="Markdown"
        )

# Обработчик текстовых сообщений
@dp.message()
async def handle_text(message: types.Message):
    text = message.text.lower()
    
    # Если клиент написал "фото", "показать фото" и т.д.
    if any(word in text for word in ["фото", "показать фото", "посмотреть фото"]):
        await message.answer(
            "Чтобы получить фотографии продукции, напишите нашему менеджеру.",
            reply_markup=create_contact_buttons()
        )
        return

    # Остальные ответы (FAQ) — можно добавить по аналогии
    await message.answer(
        "Если у вас есть конкретный вопрос, напишите, например: "
        "'Минимальный объем заказа', 'Сорта пиломатериалов' или 'Срочная доставка'."
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
