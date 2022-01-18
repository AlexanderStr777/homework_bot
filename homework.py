import logging
import os
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def send_message(bot, message):
    """Функция отправки сообщения в чат телеграмма."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Функция запроса к API Яндекс.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if homework_statuses.status_code == HTTPStatus.OK:
        return homework_statuses.json()
    else:
        raise exceptions.InvalidHttpStatus


def check_response(response):
    """Функция проверки корректности ответа API Яндекс.Практикум."""
    timestamp = response['current_date']
    homeworks = response['homeworks']
    if homeworks is None:
        raise exceptions.KeyHomeworksIsInaccessible
    if isinstance(timestamp, int) and isinstance(homeworks, list):
        return homeworks
    else:
        raise Exception


def parse_status(homework):
    """Функция, проверяющая статус домашнего задания."""
    homework_name = homework['homework_name']
    if homework_name is None:
        raise exceptions.KeyHomeworkNameIsInaccessible
    homework_status = homework.get('status')
    if homework_status is None:
        raise exceptions.KeyHomeworkStatusIsInaccessible
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES.get(homework_status)
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        raise exceptions.UnknownHomeworkStatus


def check_tokens():
    """Функция проверки наличия токена и чат id телеграмма."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    return False


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())

        while True:
            try:
                response = get_api_answer(current_timestamp)
                homeworks = check_response(response)
                quantity_of_works = len(homeworks)
                while quantity_of_works > 0:
                    message = parse_status(homeworks[quantity_of_works - 1])
                    send_message(bot, message)
                    quantity_of_works -= 1
                current_timestamp = int(time.time())
                time.sleep(RETRY_TIME)

            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
