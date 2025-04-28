from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def make_choice_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Указать сумму", callback_data="amount")],
        [InlineKeyboardButton(text="💬 Обсудить сумму лично", callback_data="manual")],
    ])

def make_time_kb():
    # Создаем клавиатуру с временем от 12:00 до 20:00 с интервалом 30 минут
    keyboard = []
    
    # Генерация времени от 12:00 до 20:00 с шагом 30 минут
    for hour in range(12, 20):
        row = []
        for minute in [0, 30]:
            time_str = f"{hour}:{minute:02d}"
            row.append(InlineKeyboardButton(text=time_str, callback_data=time_str))
        keyboard.append(row)
    
    # Добавляем последнее время - 20:00
    keyboard.append([InlineKeyboardButton(text="20:00", callback_data="20:00")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Условия и комиссии", callback_data="show_info")],
        [InlineKeyboardButton(text="🌐 Актуальный курс", url="https://grinex.io/trading/usdta7a5")],
        [InlineKeyboardButton(text="📅 Записаться на приём", callback_data="start_registration")],
    ])

def deal_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 Сделка в USDT", callback_data="deal_usdt")],
        [InlineKeyboardButton(text="🔤 Сделка в Рублевом коде", callback_data="deal_a7a5")],
    ])
