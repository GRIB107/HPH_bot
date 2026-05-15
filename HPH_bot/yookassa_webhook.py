from flask import Flask, request
from telebot import TeleBot
import logging
import sqlite3
import json
from config import config

app = Flask(__name__)

logging.basicConfig(filename='/home/GRIB107/bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Вебхук запущен")

bot = TeleBot(config['token'])
PYTHONANYWHERE_USERNAME = "GRIB107"
ADMIN_CHAT_ID = 398165085 

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
        logging.info(f"Платёж сохранён: payment_id={payment_id}, status={status}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка SQLite: {e}")
    finally:
        conn.close()

@app.route('/yookassa_webhook', methods=['POST'])
def webhook():
    logging.info("Получен запрос на /yookassa_webhook")
    try:
        data = request.get_json()
        logging.debug(f"Данные вебхука: {data}")
        if data['event'] == 'payment.succeeded':
            payment = data['object']
            payment_id = payment['id']
            user_id = int(payment['metadata']['user_id'])
            amount = payment['amount']['value']
            currency = payment['amount']['currency']
            status = payment['status']
            description = payment['description']
            save_payment(payment_id, user_id, amount, currency, status, description)
            bot.send_message(user_id, "Оплата прошла успешно! Ваш заказ скоро будет отправлен.")
            logging.info(f"Уведомление об оплате отправлено user_id={user_id}")
            
            # Формируем сообщение для админа
            user_data = load_user(user_id)
            item_name = user_data.get('что купил', 'Неизвестный товар')
            user_name = user_data.get('имя', 'Не указано')
            user_address = user_data.get('адрес', 'Не указано')
            user_phone = user_data.get('телефон', 'Не указано')
            admin_message = (
                f"Новый заказ!\n"
                f"Пользователь: {user_name} (ID: {user_id})\n"
                f"Товар: {item_name}\n"
                f"Сумма: {amount} {currency}\n"
                f"Адрес доставки: {user_address}\n"
                f"Телефон: {user_phone}\n"
                f"Описание: {description}\n"
                f"Payment ID: {payment_id}"
            )
            bot.send_message(ADMIN_CHAT_ID, admin_message)
            logging.info(f"Уведомление админу отправлено: user_id={user_id}")
        return '', 200
    except Exception as e:
        logging.error(f"Ошибка вебхука ЮKassa: {e}", exc_info=True)
        return '', 500
