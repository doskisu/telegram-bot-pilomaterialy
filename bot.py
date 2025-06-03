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

bot = Bot(token="ВАШ_ТОКЕН")
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

# ===== ЗАПУСК КАЛЬКУЛЯТОРА =====
@dp.message_handler(lambda message: message.text == "Калькулятор объемов 📐")
async def start_calculator(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for key, mat in MATERIALS.items():
        keyboard.add(InlineKeyboardButton(mat["name"], callback_data=f"calc_{key}"))
    
    await message.answer("Выберите материал:", reply_markup=keyboard)
    await CalculatorStates.waiting_material.set()

# ===== ВЫБОР МАТЕРИАЛА =====
@dp.callback_query_handler(lambda c: c.data.startswith('calc_'), state=CalculatorStates.waiting_material)
async def select_material(callback_query: types.CallbackQuery, state: FSMContext):
    material_key = callback_query.data.split('_')[1]
    await state.update_data(material=material_key)
    
    mat_data = MATERIALS[material_key]
    
    if "sizes" in mat_data:  # Для досок с выбором размера
        keyboard = InlineKeyboardMarkup(row_width=2)
        for size in mat_data["sizes"]:
            keyboard.add(InlineKeyboardButton(size, callback_data=f"size_{size}"))
        await bot.send_message(callback_query.from_user.id, "Выберите размер:", reply_markup=keyboard)
        await CalculatorStates.next()
    else:  # Для бруска/рейки (фиксированный размер)
        await bot.send_message(callback_query.from_user.id, f"Введите количество штук ({mat_data['name']}):")
        await state.update_data(size=mat_data["size"])
        await CalculatorStates.waiting_quantity.set()

# ===== ВЫБОР РАЗМЕРА (ТОЛЬКО ДЛЯ ДОСОК) =====
@dp.callback_query_handler(lambda c: c.data.startswith('size_'), state=CalculatorStates.waiting_size)
async def select_size(callback_query: types.CallbackQuery, state: FSMContext):
    size = callback_query.data.split('_')[1]
    await state.update_data(size=size)
    await bot.send_message(callback_query.from_user.id, "Введите количество штук:")
    await CalculatorStates.next()

# ===== РАСЧЕТ ОБЪЕМА =====
@dp.message_handler(state=CalculatorStates.waiting_quantity)
async def calculate_volume(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError
            
        data = await state.get_data()
        size_key = data["size"].replace("x", "").lower()
        
        # Находим коэффициент по ключу размера
        volume_coeff = next((v for k, v in VOLUME_COEFFICIENTS.items() 
                            if size_key in k.replace("x", "").lower()), None)
        
        if volume_coeff:
            total_volume = round(quantity * volume_coeff, 2)
            material_name = MATERIALS[data["material"]]["name"]
            
            # Расчет стоимости доставки (пример: 1500 руб/м³)
            delivery_cost = total_volume * 1500
            
            response = (
                f"📐 Результаты расчета:\n"
                f"• Материал: {material_name} ({data['size']})\n"
                f"• Количество: {quantity} шт\n"
                f"• Общий объем: {total_volume} м³\n"
                f"• Примерная стоимость доставки: {delivery_cost:.0f} руб\n\n"
                f"*Для точного расчета заказа свяжитесь с менеджером"
            )
            
            await message.answer(response, reply_markup=main_menu_keyboard())
        else:
            await message.answer("Ошибка: размер не найден. Попробуйте снова.")
            
    except ValueError:
        await message.answer("Пожалуйста, введите целое число больше 0!")
        return
    
    await state.finish()

# ===== ОСТАЛЬНАЯ ЛОГИКА БОТА (из предыдущего кода) =====
# ... [Обработчики для связи с менеджером, фото и т.д.] ...

# ===== ЗАПУСК =====
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
