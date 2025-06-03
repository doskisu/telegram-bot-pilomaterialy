from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

bot = Bot(token="ВАШ_ТОКЕН")
dp = Dispatcher(bot)

# ===== ОСНОВНОЕ МЕНЮ (REPLY-КЛАВИАТУРА) =====
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Связаться с менеджером 📞")],
            [KeyboardButton(text="Запросить фото 📷")]
        ]
    )

# ===== ИНЛАЙН-КНОПКИ =====
def generate_inline_buttons():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Связаться с менеджером", callback_data="contact_manager"),
        InlineKeyboardButton("Запросить фото", callback_data="request_photo")
    )

# ===== ОБРАБОТЧИК КОМАНДЫ /start =====
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🏠 Добро пожаловать! Я помогу вам с выбором пиломатериалов:\n\n"
        "- Хвойные породы (сосна, ель)\n"
        "- Доска 1/2 сорта, брусок, рейка\n"
        "- Доставка по Московской области\n\n"
        "Выберите действие 👇"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

# ===== ОБРАБОТЧИКИ КНОПОК =====
@dp.message_handler(lambda message: message.text == "Связаться с менеджером 📞")
async def contact_manager(message: types.Message):
    contact_info = (
        "📞 Контакты менеджера:\n"
        "Телефон: +7 (999) 123-45-67\n"
        "Email: manager@lesopilka.ru\n\n"
        "⏱ Часы работы: Пн-Пт 9:00-18:00\n\n"
        "Нажмите кнопку для звонка:"
    )
    
    await message.answer(
        contact_info,
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Позвонить", url="tel:+79991234567")
        )
    )

@dp.message_handler(lambda message: message.text == "Запросить фото 📷")
async def request_photo(message: types.Message):
    await message.answer(
        "Выберите материал для фото:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton("Доска 1 сорт", callback_data="photo_board1"),
                    InlineKeyboardButton("Доска 2 сорт", callback_data="photo_board2")
                ],
                [
                    InlineKeyboardButton("Брусок 50x50", callback_data="photo_bar"),
                    InlineKeyboardButton("Рейка 25x50", callback_data="photo_lath")
                ]
            ]
        )
    )

# ===== ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК =====
@dp.callback_query_handler(lambda c: c.data == "contact_manager")
async def process_callback_contact(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "✅ Менеджер свяжется с вами в течение 15 минут"
    )

@dp.callback_query_handler(lambda c: c.data.startswith('photo_'))
async def send_photos(callback_query: types.CallbackQuery):
    material = callback_query.data.split('_')[1]
    # Здесь будет логика отправки фото
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        f"Фото материала {material} отправлены в следующем сообщении..."
    )
    # Пример отправки фото:
    # await bot.send_photo(callback_query.from_user.id, photo=open(f'{material}.jpg', 'rb'))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
