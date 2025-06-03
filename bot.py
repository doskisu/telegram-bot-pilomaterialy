from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

bot = Bot(token="ВАШ_ТОКЕН_БОТА")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ===== СОСТОЯНИЯ ДЛЯ КАЛЬКУЛЯТОРА =====
class CalculatorStates(StatesGroup):
    waiting_material = State()
    waiting_size = State()
    waiting_quantity = State()

# ===== ДАННЫЕ ДЛЯ РАСЧЕТОВ =====
MATERIALS = {
    "board1": {"name": "Доска 1 сорт 6м", "sizes": ["25x100", "25x150", "40x100", "40x150", "40x200", "50x100", "50x150", "50x200"]},
    "board2": {"name": "Доска 2 сорт", "sizes": ["25x100x3м", "25x100x6м", "25x150x3м", "25x150x6м"]},
    "bar": {"name": "Брусок 50x50x3м", "size": "50x50x3000"},
    "lath": {"name": "Рейка 25x50x3м", "size": "25x50x3000"}
}

# Коэффициенты перевода (штук в м³)
VOLUME_COEFFICIENTS = {
    "25x100x6000": 0.015,   # 1 м³ = 66.6 шт
    "25x150x6000": 0.0225,  # 1 м³ = 44.4 шт
    "40x100x6000": 0.024,   # 1 м³ = 41.6 шт
    "40x150x6000": 0.036,   # 1 м³ = 27.7 шт
    "40x200x6000": 0.048,   # 1 м³ = 20.8 шт
    "50x100x6000": 0.03,    # 1 м³ = 33.3 шт
    "50x150x6000": 0.045,   # 1 м³ = 22.2 шт
    "50x200x6000": 0.06,    # 1 м³ = 16.6 шт
    "25x100x3000": 0.0075,  # 1 м³ = 133.3 шт
    "25x150x3000": 0.01125, # 1 м³ = 88.8 шт
    "50x50x3000": 0.0075,   # 1 м³ = 133.3 шт (брусок)
    "25x50x3000": 0.00375   # 1 м³ = 266.6 шт (рейка)
}

# Создаем нормализованный словарь коэффициентов
NORMALIZED_COEFFS = {}
for key, value in VOLUME_COEFFICIENTS.items():
    normalized_key = key.lower().replace("x", "").replace(" ", "")
    NORMALIZED_COEFFS[normalized_key] = value

# ===== ОСНОВНОЕ МЕНЮ =====
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Калькулятор объемов 📐")],
            [KeyboardButton(text="Связаться с менеджером 📞"), 
             KeyboardButton(text="Запросить фото 📷")]
        ]
    )

# ===== ИНЛАЙН-КНОПКИ ДЛЯ ФОТО =====
def photo_materials_keyboard():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("Доска 1 сорт", callback_data="photo_board1"),
        InlineKeyboardButton("Доска 2 сорт", callback_data="photo_board2"),
        InlineKeyboardButton("Брусок 50x50", callback_data="photo_bar"),
        InlineKeyboardButton("Рейка 25x50", callback_data="photo_lath")
    )

# ===== ОБРАБОТЧИК КОМАНДЫ /start =====
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_text = (
        "🏠 Добро пожаловать! Я бот компании Лесопилка.\n"
        "Помогу вам с выбором пиломатериалов:\n\n"
        "- Хвойные породы (сосна, ель)\n"
        "- Доска 1/2 сорта, брусок, рейка\n"
        "- Доставка по Московской области\n\n"
        "Выберите действие 👇"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

# ===== ОБРАБОТЧИКИ ОСНОВНОГО МЕНЮ =====

# Калькулятор объемов
@dp.message_handler(lambda message: message.text == "Калькулятор объемов 📐")
async def start_calculator(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for key, mat in MATERIALS.items():
        keyboard.add(InlineKeyboardButton(mat["name"], callback_data=f"calc_{key}"))
    
    await message.answer("Выберите материал:", reply_markup=keyboard)
    await CalculatorStates.waiting_material.set()

# Связаться с менеджером
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

# Запросить фото
@dp.message_handler(lambda message: message.text == "Запросить фото 📷")
async def request_photo(message: types.Message):
    await message.answer(
        "Выберите материал для фото:",
        reply_markup=photo_materials_keyboard()
    )

# ===== ОБРАБОТЧИКИ ДЛЯ КАЛЬКУЛЯТОРА =====

# Выбор материала
@dp.callback_query_handler(lambda c: c.data.startswith('calc_'), state=CalculatorStates.waiting_material)
async def select_material(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    material_key = callback_query.data.split('_')[1]
    await state.update_data(material=material_key)
    
    mat_data = MATERIALS[material_key]
    
    if "sizes" in mat_data:  # Для досок с выбором размера
        keyboard = InlineKeyboardMarkup(row_width=2)
        for size in mat_data["sizes"]:
            keyboard.add(InlineKeyboardButton(size, callback_data=f"size_{size}"))
        await bot.send_message(callback_query.from_user.id, "Выберите размер:", reply_markup=keyboard)
        await CalculatorStates.waiting_size.set()
    else:  # Для бруска/рейки (фиксированный размер)
        await bot.send_message(callback_query.from_user.id, f"Введите количество штук ({mat_data['name']}):")
        await state.update_data(size=mat_data["size"])
        await CalculatorStates.waiting_quantity.set()

# Выбор размера (только для досок)
@dp.callback_query_handler(lambda c: c.data.startswith('size_'), state=CalculatorStates.waiting_size)
async def select_size(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    
    size = callback_query.data.split('_')[1]
    await state.update_data(size=size)
    await bot.send_message(callback_query.from_user.id, "Введите количество штук:")
    await CalculatorStates.waiting_quantity.set()

# Расчет объема
@dp.message_handler(state=CalculatorStates.waiting_quantity)
async def calculate_volume(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
            
        data = await state.get_data()
        material_key = data["material"]
        size = data["size"]
        
        # Формируем ключ для коэффициента
        size_key = size
        
        # Для разных типов материалов формируем ключ по-разному
        if material_key == "board1":
            size_key = f"{size}x6000"
        elif material_key == "board2":
            if "3м" in size:
                size_key = size.replace("3м", "3000")
            elif "6м" in size:
                size_key = size.replace("6м", "6000")
        
        # Нормализуем ключ для поиска
        normalized_key = size_key.lower().replace("x", "").replace(" ", "")
        
        # Получаем коэффициент объема
        volume_coeff = NORMALIZED_COEFFS.get(normalized_key)
        
        if volume_coeff:
            total_volume = round(quantity * volume_coeff, 3)
            material_name = MATERIALS[material_key]["name"]
            
            # Расчет стоимости (примерные цены)
            material_price = 15000  # руб/м³
            delivery_price = 1500   # руб/м³
            
            material_cost = total_volume * material_price
            delivery_cost = total_volume * delivery_price
            total_cost = material_cost + delivery_cost
            
            response = (
                f"📐 Результаты расчета:\n"
                f"• Материал: {material_name} ({size})\n"
                f"• Количество: {quantity} шт\n"
                f"• Общий объем: {total_volume} м³\n\n"
                f"💰 Примерная стоимость:\n"
                f"• Материал: {material_cost:.0f} руб\n"
                f"• Доставка: {delivery_cost:.0f} руб\n"
                f"• Итого: {total_cost:.0f} руб\n\n"
                f"*Для точного расчета заказа свяжитесь с менеджером"
            )
            
            await message.answer(response, reply_markup=main_menu_keyboard())
        else:
            await message.answer(f"❌ Ошибка: для размера '{size_key}' не найден коэффициент объема.", 
                               reply_markup=main_menu_keyboard())
            
    except ValueError:
        await message.answer("⚠️ Пожалуйста, введите целое положительное число!")
        return
    
    await state.finish()

# ===== ОБРАБОТЧИКИ ДЛЯ ФОТО =====
@dp.callback_query_handler(lambda c: c.data.startswith('photo_'))
async def send_photos(callback_query: types.CallbackQuery):
    material_type = callback_query.data.split('_')[1]
    
    # Текстовые описания для каждого материала
    descriptions = {
        "board1": "Доска 1 сорта, 6 метров. Идеальная геометрия, минимум сучков.",
        "board2": "Доска 2 сорта. Подходит для черновых работ. Допускается небольшой обзол.",
        "bar": "Брусок 50x50 мм, длина 3 метра. Используется для каркасов и обрешетки.",
        "lath": "Рейка 25x50 мм, длина 3 метра. Применяется в отделочных работах."
    }
    
    material_names = {
        "board1": "Доска 1 сорт",
        "board2": "Доска 2 сорт",
        "bar": "Брусок 50x50",
        "lath": "Рейка 25x50"
    }
    
    try:
        name = material_names.get(material_type, "Пиломатериал")
        description = descriptions.get(material_type, "Фото материала")
        
        # В реальном боте используйте:
        # await bot.send_photo(
        #     chat_id=callback_query.from_user.id,
        #     photo=open(f"photos/{material_type}.jpg", "rb"),
        #     caption=f"{name}\n{description}"
        # )
        
        # Заглушка для примера:
        await bot.send_message(
            callback_query.from_user.id,
            f"📸 {name}\n{description}\n\n"
            "В реальном боте здесь будет отправлено фото."
        )
        
        await bot.answer_callback_query(callback_query.id)
    except Exception as e:
        await bot.send_message(callback_query.from_user.id, f"❌ Ошибка при отправке фото: {str(e)}")
        await bot.answer_callback_query(callback_query.id, "Произошла ошибка", show_alert=True)

# ===== ОБРАБОТКА ДРУГИХ СООБЩЕНИЙ =====
@dp.message_handler()
async def handle_other_messages(message: types.Message):
    await message.answer(
        "Пожалуйста, используйте кнопки меню для навигации:",
        reply_markup=main_menu_keyboard()
    )

# ===== ЗАПУСК БОТА =====
if __name__ == '__main__':
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
