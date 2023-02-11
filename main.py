import logging
import os
import sys
from http import HTTPStatus
import requests
import time
import telegram
from binance.client import Client
from dotenv import load_dotenv

from exceptions import OurRequestError, NotSendmessageException

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_ID')
API_KEY = os.getenv('API_TOKEN')
API_SECRET = os.getenv('SEKRET_KEY')

RETRY_PERIOD = 60
PROCENT_CHANGE = 0.99


def check_tokens():
    """Проверяем наличие токенов."""
    CHECK_TOKENS = {
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
        'api_key': API_KEY,
        'api_secret': API_SECRET,
    }
    for key, value in CHECK_TOKENS.items():
        if not value:
            logging.critical(f'Token {key} отсутствует')
            return False
    logging.info('Token. Токены найдены')
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Send message {message}  in {TELEGRAM_CHAT_ID} chat!')
    except telegram.error.TelegramError:
        logging.error('Ошибка при отправке сообщения')
        raise NotSendmessageException('Сообщение успешно отправлено')


def get_api_answer(client):
    """Получаем ответ от API."""
    try:
        klines = client.get_historical_klines(
            "BNBBUSD",
            Client.KLINE_INTERVAL_1HOUR,
            "1 hour ago UTC")
        return klines
    except requests.exceptions.RequestException:
        message = f'Ошибка при запросе к API.'
        logging.error(message)
    except requests.exceptions.RequestException as error:
        message = 'Ошибка при запросе к API.'
        logging.error(message)
        raise OurRequestError(message) from error


def main():
    """Основная логика работы бота."""
    logging.info('Бот пытается запустится')
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logging.info('Бот запустился')
        client = Client(API_KEY, API_SECRET)

        while True:
            try:
                # Сделать запрос к API binance
                response = get_api_answer(client)
                logging.info("List of homework received")
                # Проверить ответ.
                max_price = float(response[0][2])
                now_price = float(response[0][4])
                if now_price > max_price * PROCENT_CHANGE:
                    message = (f"Динь-дон, цена упала и составляет {now_price}. Это {now_price*100/max_price:.2f}% от максимума")
                    send_message(bot, message)
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
            finally:
                time.sleep(RETRY_PERIOD)
    else:
        logging.critical('Бот не запущен, нет токенок')
        sys.exit(1)


if __name__ == '__main__':
    main()
