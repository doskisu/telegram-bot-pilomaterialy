import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Логирование
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения
API_TOKEN = os.getenv('BOT_TOKEN')
MANAGER_TELEGRAM_ID = 'raszd189'  # Telegram-никнейм менеджера

# Инициализируем бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Кнопки для бота
def create_buttons():
    buttons = [
        [InlineKeyboardButton(text="📞 Связаться с менеджером", url=f"https://t.me/{MANAGER_TELEGRAM_ID}")], 
        [InlineKeyboardButton(text="📷 Запросить фото", callback_data="request_photo")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для заказа пиломатериалов. Вот что я могу:\n\n"
        "- Ответить на вопросы о продукции\n"
        "- Предоставить контакты менеджера\n"
        "- Показать фото продукции",
        reply_markup=create_buttons()
    )

# Обработчик нажатий на кнопки
@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    if callback_query.data == "request_photo":
        await callback_query.message.answer(
            "Чтобы получить фотографии продукции, свяжитесь с нашим менеджером: "
            f"[https://t.me/{MANAGER_TELEGRAM_ID}](https://t.me/{MANAGER_TELEGRAM_ID})", 
            parse_mode="Markdown"
        )

# Обработчик текстовых сообщений
@dp.message()
async def handle_text(message: types.Message):
    user_text = message.text.lower()

    # База знаний: вопросы и ответы
    faq = {
        "какой тип|вид|что предлагаете": (
            "Мы предлагаем обрезные хвойные пиломатериалы (сосна, ель) естественной влажности стандартных размеров. "
            "Также производим брусок 50×50×3 м и рейку 25×50×3 м. "
            "Есть доска 2-го сорта размерами 25×100 и 25×150 (длиной 3 или 6 метров)."
        ),
        "сорта|какие сорта": (
            "Мы производим пиломатериалы 1-го и 2-го сортов. "
            "Доска 2-го сорта имеет хорошую геометрию, но содержит больше обзола, из-за чего стоит дешевле."
        ),
        "минимальный объем|сколько минимум заказать": (
            "Минимальный объем заказа:\n"
            "- Для стандартных пиломатериалов: **40 кубов**.\n"
            "- Для трехмеровых пиломатериалов: **33 куба**."
        ),
        "оплата|как платить": (
            "Мы работаем как по наличному, так и по безналичному расчету. "
            "Оплата возможна с НДС и без НДС. Также принимаем оплату наличными."
        ),
        "где находится|производство|ваш завод": (
            "Наши производства расположены в Тверской и Владимирской областях."
        ),
        "объем производства|сколько выпускаете": (
            "Объем производства составляет более 5000 тыс. кубов в месяц."
        ),
        "сроки доставки|когда доставят": (
            "Сроки доставки согласовываются индивидуально. При необходимости можем организовать срочную доставку."
        ),
        "нестандартные размеры|можно ли заказать": (
            "Мы производим пиломатериалы стандартных размеров. "
            "При покупке трехмеровых пиломатериалов минимальный объем заказа — 33 куба."
        ),
        "что такое доска 2-го сорта|доска 2 сорта": (
            "Доска 2-го сорта имеет хорошую геометрию, но содержит немного больше обзола, из-за чего стоит дешевле. "
            "Размеры: 25×100 мм и 25×150 мм, длина: 3 или 6 метров. Подходит для черновых работ."
        ),
        "официально|через фгис": (
            "Да, мы работаем официально через ФГИС (Федеральную государственную информационную систему)."
        ),
        "связаться|менеджер|срочная консультация": (
            "Если вам нужна срочная консультация, свяжитесь с нашим менеджером: "
            f"[https://t.me/{MANAGER_TELEGRAM_ID}](https://t.me/{MANAGER_TELEGRAM_ID}).  "
            "Либо оставьте свой номер телефона, и мы свяжемся с вами."
        )
    }

    # Поиск ответа в базе знаний
    for keywords, answer in faq.items():
        if any(keyword in user_text for keyword in keywords.split('|')):
            await message.answer(answer, reply_markup=create_buttons())
            return

    # Если ничего не найдено
    await message.answer(
        "Я не понял ваш вопрос. Вот что я могу:\n\n"
        "- Рассказать о типах пиломатериалов\n"
        "- Сообщить минимальный объем заказа\n"
        "- Предоставить контакты менеджера\n\n"
        "Напишите, например: 'Минимальный объем заказа' или 'Какие сорта доступны'.",
        reply_markup=create_buttons()
    )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
