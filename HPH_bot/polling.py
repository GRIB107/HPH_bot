from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from os import path
import logging
import sqlite3
import uuid
import json
from yookassa import Configuration, Payment
from utils import load_json_data, dict_to_str
from config import config
from random import randint


logging.basicConfig(filename='/home/GRIB107/bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Polling запущен")

bot = TeleBot(config['token'])
SHOP_ID = "1121371"
SECRET_KEY = "test_du0r-_BM6F0fdXIPgptHilj5vtGMRRBPqBjxBJpFyW4"
PYTHONANYWHERE_USERNAME = "GRIB107"
Configuration.configure(SHOP_ID, SECRET_KEY)

main_dir = path.dirname(path.dirname(__file__))
media_dir = path.join(main_dir, 'storage')
filename = path.join(media_dir, 'data.json')
users = {}
order = (1, 1000000)

def save_json_data(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Данные сохранены в {filename}")
    except Exception as e:
        logging.error(f"Ошибка сохранения данных в {filename}: {e}")

def init_db():
    try:
        conn = sqlite3.connect(f'/home/{PYTHONANYWHERE_USERNAME}/payments.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id TEXT PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                currency TEXT,
                status TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()
        logging.info("База данных инициализирована")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
    finally:
        conn.close()

def save_user(user_id, user_data):
    try:
        conn = sqlite3.connect(f'/home/{PYTHONANYWHERE_USERNAME}/payments.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(user_data)))
        conn.commit()
        logging.info(f"Пользователь сохранён: user_id={user_id}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка сохранения пользователя user_id={user_id}: {e}")
    finally:
        conn.close()

def load_user(user_id):
    try:
        conn = sqlite3.connect(f'/home/{PYTHONANYWHERE_USERNAME}/payments.db')
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return json.loads(result[0])
        return {}
    except sqlite3.Error as e:
        logging.error(f"Ошибка загрузки пользователя user_id={user_id}: {e}")
        return {}

def save_payment(payment_id, user_id, amount, currency, status, description):
    try:
        conn = sqlite3.connect(f'/home/{PYTHONANYWHERE_USERNAME}/payments.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO payments (payment_id, user_id, amount, currency, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (payment_id, user_id, amount, currency, status, description))
        conn.commit()
        logging.info(f"Платёж сохранён: {payment_id}, status={status}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
    finally:
        conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    logging.info(f"Получена команда /start от user_id={message.from_user.id}, chat_id={message.chat.id}")
    users = load_user(message.from_user.id)
    if not users:
        users = {}
        save_user(message.from_user.id, users)
    try:
        text = 'Здесь ты можешь купить акулку'
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(text='Купить акулку', callback_data='Купить'),
            InlineKeyboardButton(text='Прочитай меня', callback_data='Инфо')
        )
        bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML', reply_markup=markup)
        logging.info(f"Ответ отправлен user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка отправки ответа user_id={message.from_user.id}: {e}", exc_info=True)

@bot.message_handler(commands=['info'])
def send_info(message: Message):
    logging.info(f"Получена команда /info от user_id={message.from_user.id}")
    try:
        voskl = u"\u203C"
        text = f"{voskl}Перед покупкой <b><u>ВНИМАТЕЛЬНО</u></b> прочитай это сообщение! \n\nВсе цены в этом боте указаны за 1 шт. товара <b>БЕЗ УЧЁТА СТОИМОСТИ ДОСТАВКИ</b>. Доставка оплачивается в 100% размере <u>самим покупателем</u>.\nПримерная стоимость доставки в разные регионы страны будет указана при оплате"
        bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML')
        logging.info(f"Ответ отправлен user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка отправки ответа user_id={message.from_user.id}: {e}", exc_info=True)

@bot.message_handler(commands=['other'])
def send_other(message: Message):
    logging.info(f"Получена команда /other от user_id={message.from_user.id}")
    try:
        emoji = u"\U0001F609"
        text = f"Напиши ниже, какое впечатление у тебя от нашего бота? Что бы ты хотел исправить или добавить?\nТакже сюда пиши по поводу сотрудничества с нами. \nТвоё сообщение обязательно прочитает разработчик, будь уверен {emoji}"
        bot.send_message(chat_id=message.chat.id, text=text, parse_mode='HTML')
        logging.info(f"Ответ отправлен user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка отправки ответа user_id={message.from_user.id}: {e}", exc_info=True)

@bot.callback_query_handler(func=lambda call: call.data == 'Купить')
def button_buy(call: CallbackQuery):
    logging.info(f"Получен callback Купить от user_id={call.from_user.id}")
    try:
        data = load_json_data(filename)
        has_items = False
        for i in range(len(data)):
            item = data[i]
            if item[2] > 0:  # Показываем только товары в наличии
                has_items = True
                listok = dict_to_str(item[3])
                put = path.join(main_dir, item[1])
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(InlineKeyboardButton(text='Купить', callback_data=f'купить {i}'))
                with open(put, 'rb') as photo:
                    bot.send_photo(call.from_user.id, photo, caption=listok + f"\n<b>Имеется в наличии:</b> {item[2]}", parse_mode='HTML', reply_markup=markup)
        if not has_items:
            bot.send_message(call.from_user.id, "К сожалению, товары закончились.")
        bot.answer_callback_query(call.id)
        logging.info(f"Фотографии отправлены user_id={call.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка обработки Купить user_id={call.from_user.id}: {e}", exc_info=True)

@bot.callback_query_handler(func=lambda call: call.data == 'Инфо')
def button_info(call: CallbackQuery):
    logging.info(f"Получен callback Инфо от user_id={call.from_user.id}")
    try:
        voskl = u"\u203C"
        text = f"{voskl}Перед покупкой <b><u>ВНИМАТЕЛЬНО</u></b> прочитай это сообщение! \n\nВсе цены в этом боте указаны за 1 шт. товара <b>БЕЗ УЧЁТА СТОИМОСТИ ДОСТАВКИ</b>. Доставка оплачивается в 100% размере <u>самим покупателем</u> при получении товара.\nПримерная стоимость доставки в разные регионы страны будет указана при оплате\n\n\n<u><b>ТОВАР ВОЗВРАТУ И ОБМЕНУ НЕ ПОДЛЕЖИТ</b></u>"
        bot.send_message(call.from_user.id, text=text, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        logging.info(f"Ответ отправлен user_id={call.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка обработки Инфо user_id={call.from_user.id}: {e}", exc_info=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('купить '))
def button_buy_item(call: CallbackQuery):
    logging.info(f"Получен callback {call.data} от user_id={call.from_user.id}")
    try:
        data = load_json_data(filename)
        number = int(call.data.split()[1])
        if number >= len(data) or data[number][2] <= 0:
            bot.send_message(call.from_user.id, "Этот товар закончился или недоступен.")
            bot.answer_callback_query(call.id)
            return
        users = load_user(call.from_user.id)
        users['что купил'] = data[number][3]["Название"]
        users['item_index'] = number  # Сохраняем индекс товара для вебхука
        save_user(call.from_user.id, users)
        voskl = u"\u203C"
        text = f"{voskl}Перед покупкой <b><u>ВНИМАТЕЛЬНО</u></b> прочитай это сообщение! \n\nВсе цены в этом боте указаны за 1 шт. товара <b>БЕЗ УЧЁТА СТОИМОСТИ ДОСТАВКИ</b>. Доставка оплачивается в 100% размере <u>самим покупателем</u> при получении товара.\nПримерная стоимость доставки по регионам РФ:\n<b>Москва</b> - 249 руб.\n<b>Краснодар</b> - 269 руб.\n<b>Челябинск</b> - 259 руб.\n<b>Новосибирск</b> - 269 руб.\n"
        bot.send_message(call.from_user.id, text=text, parse_mode='HTML')
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(text='Я всё прочитал и понял. Хочу купить', callback_data='точно'))
        text1 = 'Обращаем ваше внимание, что <u><b>ТОВАР ВОЗВРАТУ И ОБМЕНУ НЕ ПОДЛЕЖИТ</b></u>\n\nВ случае неоплаты покупателем стоимости доставки на пункте выдачи, в результате которой товар будет возвращён автоматически, уплаченные средства за товар <b>возврату не подлежат</b>\n\nЗа порчу/утерю товара по вине доставки администрация данного бота <u>ответственности не несёт</u>'
        bot.send_message(call.from_user.id, text=text1, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        logging.info(f"Сообщения отправлены user_id={call.from_user.id}")
    except ValueError as e:
        logging.error(f"Ошибка обработки покупки user_id={call.from_user.id}: {e}", exc_info=True)
        bot.send_message(call.from_user.id, "Ошибка: неверный формат данных. Попробуйте снова.")
        bot.answer_callback_query(call.id)
    except Exception as e:
        logging.error(f"Ошибка обработки покупки user_id={call.from_user.id}: {e}", exc_info=True)
        bot.send_message(call.from_user.id, f"Ошибка: {e}")
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'точно')
def button_buy_confirm(call: CallbackQuery):
    logging.info(f"Получен callback Купить точно от user_id={call.from_user.id}")
    try:
        bot.answer_callback_query(call.id)
        name = "На чьё имя будем высылать товар?"
        msg = bot.send_message(call.from_user.id, text=name)
        bot.register_next_step_handler(msg, save_name)
        logging.info(f"Запрос имени отправлен user_id={call.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка обработки Купить точно user_id={call.from_user.id}: {e}", exc_info=True)
        bot.send_message(call.from_user.id, f"Ошибка: {e}")

def save_name(message: Message):
    logging.info(f"Получено имя от user_id={message.from_user.id}")
    try:
        if message.content_type != 'text' or len(message.text) < 2:
            msg = bot.reply_to(message, "Умоляю, введи нормальное имя. Только текст.")
            bot.register_next_step_handler(msg, save_name)
            return
        users = load_user(message.from_user.id)
        users['имя'] = message.text
        save_user(message.from_user.id, users)
        adress = 'Теперь укажи адрес пункта выдачи, куда нужно будет доставить товар'
        msg = bot.send_message(chat_id=message.chat.id, text=adress, parse_mode='HTML')
        bot.register_next_step_handler(msg, save_adress)
        logging.info(f"Запрос адреса отправлен user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка сохранения имени user_id={message.from_user.id}: {e}", exc_info=True)
        bot.reply_to(message, f"Ошибка: {e}")

def save_adress(message: Message):
    logging.info(f"Получен адрес от user_id={message.from_user.id}")
    try:
        if message.content_type != 'text' or len(message.text) < 5:
            msg = bot.reply_to(message, "Ну неужели так сложно написать нормальный адрес? Только текст.")
            bot.register_next_step_handler(msg, save_adress)
            return
        users = load_user(message.from_user.id)
        users['адрес'] = message.text
        save_user(message.from_user.id, users)
        phone_number = 'И номер телефона для связи'
        msg = bot.send_message(chat_id=message.chat.id, text=phone_number, parse_mode='HTML')
        bot.register_next_step_handler(msg, save_phone)
        logging.info(f"Запрос телефона отправлен user_id={message.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка сохранения адреса user_id={message.from_user.id}: {e}", exc_info=True)
        bot.reply_to(message, f"Ошибка: {e}")

def save_phone(message: Message):
    logging.info(f"Получен телефон от user_id={message.from_user.id}")
    try:
        users = load_user(message.from_user.id)
        users['телефон'] = int(message.text)
        save_user(message.from_user.id, users)
        payment_id = str(uuid.uuid4())
        order = randint(1, 1000000000)
        description = f"Заказ №{order}"
        logging.info(f"Создание платежа для user_id={message.from_user.id}, payment_id={payment_id}, order={order}")
        payment = Payment.create(
            {
                "amount": {
                    "value": "200.00",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/HPH_merch_bot/return_url"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    'orderNumber': str(order),
                    "user_id": str(message.from_user.id),
                    "item_index": str(users['item_index'])  # Передаём индекс товара
                }
            }, uuid.uuid4())
        save_payment(payment_id, message.from_user.id, 200.00, "RUB", payment.status, description)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(text='Внести оплату 200 рублей', url=payment.confirmation.confirmation_url))
        bot.send_message(chat_id=message.chat.id, text='Готово! Осталось только оплатить', parse_mode='HTML', reply_markup=markup)
        logging.info(f"Ссылка на оплату отправлена user_id={message.from_user.id}")
    except ValueError:
        msg = bot.reply_to(message, "Пожалуйста, введи корректный номер телефона (только цифры).")
        bot.register_next_step_handler(msg, save_phone)
    except Exception as e:
        logging.error(f"Ошибка создания платежа user_id={message.from_user.id}: {e}", exc_info=True)
        bot.reply_to(message, f"Ошибка: {e}")

def save_payment(payment_id, user_id, amount, currency, status, description):
    try:
        conn = sqlite3.connect(f'/home/{PYTHONANYWHERE_USERNAME}/payments.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO payments (payment_id, user_id, amount, currency, status, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (payment_id, user_id, amount, currency, status, description))
        conn.commit()
        logging.info(f"Платёж сохранён: {payment_id}, user_id={user_id}, status={status}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
    finally:
        conn.close()



@bot.message_handler(content_types=['text', 'photo', 'sticker'])
def send_answer(message: Message):
    try:
        emoji = u"\U0001F920"
        bot.send_message(chat_id=message.chat.id, text=f'Неплохо! Вот это ты <s>долбоёб</s> оригинальный! {emoji} \n\n\nНе пробовал использовать мои команды?', parse_mode='HTML')
    except Exception as e:
        logging.error(f"Ошибка ответа на сообщение пользователя: {e}", exc_info=True)
        return '', 200

if __name__ == "__main__":
    init_db()
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка polling: {e}", exc_info=True)