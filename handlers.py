from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from config import ADMIN_CHAT_ID
from keyboards import make_choice_kb, make_time_kb, main_menu_kb, deal_type_kb
from utils import get_username_or_request, parse_ref
from db import save_to_db
from datetime import date

router = Router()

class Form(StatesGroup):
    method = State()
    deal_type = State()
    amount = State()
    date = State()
    time = State()
    contact = State()  # Новое состояние для запроса контактов

# Словарь для хранения сообщений об ошибках по идентификатору пользователя
error_messages = {}

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    # Приветственное сообщение с информацией
    text = (
        "Привет! Хочешь обменять наличные на USDT в Саратове?\n\n"
        "📍 Мы находимся в центре, работаем с 12:00 до 20:00\n"
        "💵 Поддерживаем рубли, доллары, swift, инвойсы\n\n"
        "📅 Хочешь записаться? Выбери день и время 👉"
    )
    # Отправка приветственного сообщения
    await message.answer(text, reply_markup=main_menu_kb())
    
    # Сохраняем username для последующего использования
    username = get_username_or_request(message.from_user)
    await state.update_data(username=username)
    
    # Сохраняем флаг наличия тега
    has_tag = message.from_user.username is not None
    await state.update_data(has_tag=has_tag)

@router.callback_query(F.data == "show_info")
async def show_info(callback: CallbackQuery):
    text = (
        "📊 *Условия обмена:*\n\n"
        "🔤 Рублёвый стейблкоин A7A5:\n"
        "- 100 000–500 000₽ → 1% комиссия\n"
        "- от 500 000₽ → 0.8%\n\n"
        "💵 USDT:\n"
        "- 100 000–500 000₽ → 1% комиссия\n"
        "- от 500 000₽ → 0.8%\n\n"
        "✅ Минимальная сумма сделки: 50 000₽\n"
        "🔐 Чистый USDT, доходит до Binance, Bybit и др."
    )
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_menu_kb())

@router.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    # Удаляем предыдущие сообщения об ошибках, если они есть
    if callback.from_user.id in error_messages:
        for msg_id in error_messages[callback.from_user.id]:
            try:
                await callback.bot.delete_message(callback.message.chat.id, msg_id)
            except Exception:
                pass
        error_messages[callback.from_user.id] = []
    
    # Сохраняем username для последующего использования
    username = get_username_or_request(callback.from_user)
    await state.update_data(username=username)
    
    # Сохраняем флаг наличия тега
    has_tag = callback.from_user.username is not None
    await state.update_data(has_tag=has_tag)
    
    calendar_message = await callback.message.answer("📅 Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())
    await state.update_data(calendar_message_id=calendar_message.message_id)
    await state.set_state(Form.date)

@router.callback_query(SimpleCalendarCallback.filter(), Form.date)
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, selected_date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        # Проверка на прошедшую дату
        if selected_date.date() < date.today():
            error_msg = await callback_query.message.answer("⛔ Вы не можете выбрать прошедшую дату. Пожалуйста, выберите другую.")
            
            # Сохраняем ID сообщения с ошибкой для последующего удаления
            user_id = callback_query.from_user.id
            if user_id not in error_messages:
                error_messages[user_id] = []
            error_messages[user_id].append(error_msg.message_id)
            
            # Получаем ID предыдущего сообщения с календарем
            data = await state.get_data()
            if 'calendar_message_id' in data:
                try:
                    await callback_query.bot.delete_message(callback_query.message.chat.id, data['calendar_message_id'])
                except Exception:
                    pass
            
            calendar_message = await callback_query.message.answer("📅 Выберите дату заново:", reply_markup=await SimpleCalendar().start_calendar())
            await state.update_data(calendar_message_id=calendar_message.message_id)
            return
            
        # Форматирование даты для красивого отображения
        formatted_date = selected_date.strftime("%d.%m.%Y")  # ДД.ММ.ГГГГ
        raw_date = selected_date.strftime("%Y-%m-%d")  # Сохраняем в системном формате
        
        await state.update_data(date=raw_date, formatted_date=formatted_date)
        
        # Удаляем сообщение с календарем
        await callback_query.message.delete()
        
        # Очищаем сообщения об ошибках
        user_id = callback_query.from_user.id
        if user_id in error_messages:
            for msg_id in error_messages[user_id]:
                try:
                    await callback_query.bot.delete_message(callback_query.message.chat.id, msg_id)
                except Exception:
                    pass
            error_messages[user_id] = []
        
        time_message = await callback_query.message.answer("🕒 Выберите удобное время:", reply_markup=make_time_kb())
        await state.update_data(time_message_id=time_message.message_id)
        await state.set_state(Form.time)

@router.callback_query(Form.time)
async def choose_time(callback: CallbackQuery, state: FSMContext):
    await state.update_data(time=callback.data)
    
    # Удаляем сообщение с выбором времени
    await callback.message.delete()
    
    deal_type_message = await callback.message.answer("💱 Какой тип сделки вы хотите совершить?", reply_markup=deal_type_kb())
    await state.update_data(deal_type_message_id=deal_type_message.message_id)
    await state.set_state(Form.deal_type)

@router.callback_query(Form.deal_type)
async def select_deal_type(callback: CallbackQuery, state: FSMContext):
    deal_type = callback.data.replace("deal_", "")
    deal_type_display = "USDT" if deal_type == "usdt" else "A7A5"
    
    # Добавляем информацию о валюте
    currency = "$" if deal_type == "usdt" else "₽"
    
    await state.update_data(
        deal_type=deal_type,
        deal_type_display=deal_type_display,
        currency=currency
    )
    
    # Удаляем сообщение с выбором типа сделки
    await callback.message.delete()
    
    # Определяем правильное описание валюты для подсказки
    currency_text = "долларах" if deal_type == "usdt" else "рублях"
    
    amount_message = await callback.message.answer("💰 Хотите указать сумму?", reply_markup=make_choice_kb())
    await state.update_data(amount_message_id=amount_message.message_id)
    await state.set_state(Form.method)

@router.callback_query(Form.method)
async def choose_method(callback: CallbackQuery, state: FSMContext):
    # Удаляем сообщение с выбором метода
    await callback.message.delete()
    
    data = await state.get_data()
    currency_text = "долларах" if data.get('deal_type') == "usdt" else "рублях"
    
    if callback.data == "amount":
        amount_input_message = await callback.message.answer(f"💰 Введите сумму обмена (в {currency_text}):")
        await state.update_data(amount_input_message_id=amount_input_message.message_id)
        await state.set_state(Form.amount)
    else:  # callback.data == "manual"
        # Если не указать сумму, то делаем пропуск и заявку с "Не указано"
        await state.update_data(amount='Не указано', has_amount=False)
        data = await state.get_data()
        
        # Генерируем итоговое сообщение
        await generate_final_message(callback.message, state, data)

@router.message(Form.amount)
async def get_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    
    # Проверка на ввод чисел
    if not text.isdigit():
        error_msg = await message.answer("🚫 Введите только цифры без символов. Попробуйте снова:")
        
        # Сохраняем ID сообщения с ошибкой
        user_id = message.from_user.id
        if user_id not in error_messages:
            error_messages[user_id] = []
        error_messages[user_id].append(error_msg.message_id)
        return
    
    amount = int(text)
    data = await state.get_data()
    is_usdt = data.get('deal_type') == "usdt"
    
    # Проверка на минимальную сумму (50000 рублей или эквивалент в USD)
    min_amount = 500 if is_usdt else 50000  # Предполагаем, что 1 USD = 100 RUB для простоты
    if amount < min_amount:
        min_display = min_amount
        currency_text = "долларах" if is_usdt else "рублях"
        error_msg = await message.answer(f"⚠️ Минимальная сумма — {min_display} {data.get('currency', '₽')}. Попробуйте снова:")
        
        # Сохраняем ID сообщения с ошибкой
        user_id = message.from_user.id
        if user_id not in error_messages:
            error_messages[user_id] = []
        error_messages[user_id].append(error_msg.message_id)
        return

    # Очищаем сообщения об ошибках
    user_id = message.from_user.id
    if user_id in error_messages:
        for msg_id in error_messages[user_id]:
            try:
                await message.bot.delete_message(message.chat.id, msg_id)
            except Exception:
                pass
        error_messages[user_id] = []

    # Удаляем сообщение с запросом ввода суммы
    if 'amount_input_message_id' in data:
        try:
            await message.bot.delete_message(message.chat.id, data['amount_input_message_id'])
        except Exception:
            pass

    # Форматируем сумму для красивого отображения
    formatted_amount = f"{amount:,}".replace(",", " ")
    
    await state.update_data(amount=str(amount), formatted_amount=formatted_amount, has_amount=True)
    data = await state.get_data()
    
    # Генерируем итоговое сообщение
    await generate_final_message(message, state, data)

async def generate_final_message(message, state, data):
    # Получаем информацию о наличии тега
    has_tag = data.get('has_tag', False)
    username = data.get('username', f"ID: {message.from_user.id}")
    
    # Получаем форматированные данные или используем запасные варианты
    formatted_date = data.get('formatted_date', data.get('date', 'не указана'))
    time = data.get('time', 'не указано')
    deal_type_display = data.get('deal_type_display', data.get('deal_type', 'не указано').upper())
    
    # Форматируем сумму, если она есть
    amount = data.get('amount', 'Не указано')
    has_amount = data.get('has_amount', False) if amount != 'Не указано' else False
    
    # Определяем отображение суммы с валютой или без
    if has_amount:
        currency = data.get('currency', '')
        amount_display = f"{data.get('formatted_amount', amount)} {currency}"
    else:
        amount_display = "Не указано"
    
    # Базовое сообщение об успешной записи
    text = (
        f"✅ *Заявка успешно оформлена!*\n\n"
        f"📝 *Детали заявки:*\n"
        f"• Тип сделки: *{deal_type_display}*\n"
        f"• Сумма: *{amount_display}*\n"
        f"• Дата: *{formatted_date}*\n"
        f"• Время: *{time}*\n"
    )
    
    # Добавляем разные сообщения в зависимости от наличия тега
    if has_tag:
        text += (
            f"\n✨ Отлично! Наш менеджер свяжется с вами через Telegram "
            f"в течение 30 минут для подтверждения заявки."
        )
    else:
        text += (
            f"\n⚠️ Для связи с вами, пожалуйста, напишите нам в личные сообщения: "
            f"@FedulAI или укажите свой номер телефона для связи."
        )
    
    await message.answer(text, parse_mode="Markdown")
    
    # Отправляем уведомление администратору
    try:
        admin_text = (
            f"🔔 *Новая заявка!*\n\n"
            f"👤 Клиент: {username}\n"
            f"💱 Тип сделки: {deal_type_display}\n"
            f"💰 Сумма: {amount_display}\n"
            f"📅 Дата: {formatted_date}\n"
            f"🕒 Время: {time}\n"
        )
        await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="Markdown")
    except Exception:
        # Если не удалось отправить уведомление, продолжаем работу
        pass
    
    # Очищаем состояние
    await state.clear()
