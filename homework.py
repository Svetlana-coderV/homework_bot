import logging
import os
import time

from lib2to3.pgen2.tokenize import TokenError
from urllib.error import URLError

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)

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


def send_message(bot, message):
    """Функция отправки сообщений."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = parse_status()
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Удачная отправка сообщения {message}')
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения {message}')


def get_api_answer(current_timestamp):
    """
    Функция делает запрос к эндпоинту
    и возвращает ответ в формате данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        logging.error(f'Эндпоинт {ENDPOINT} недоступен')
        raise URLError('API возвращает статус-код != 200')


def check_response(response):
    """Функция проверки ответа API."""
    if type(response) is dict:
        if 'homeworks' in response:
            homeworks = response.get('homeworks')
            if type(homeworks) is list:
                return homeworks
            else:
                logging.error(
                    'под ключом `homeworks` домашки'
                    'приходят не в виде списка в ответ от API'
                )
                raise TypeError('homeworks - не словарь')
        else:
            logging.error('Ответ API не содержит ключ \'homeworks\'')
            raise KeyError('Ответ API не содержит ключ \'homeworks\'')
    else:
        logging.error('Формат ответа API - не словарь')
        raise TypeError('Формат ответа API - не словарь')


def parse_status(homework):
    """Функция парсинга статуса конкретной homework из списка homeworks."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES.keys():
        logging.error('Неизвестный статус домашки в ответе API')
        raise KeyError('Неизвестный статус домашки в ответе API')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки переменных окружения."""
    env_list = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    for env in env_list:
        if globals()[env] is None:
            logging.critical('Не найдены переменные окружения')
            return False
        return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise TokenError('Не пройдена проверка переменных окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                status_message = parse_status(homework)
            current_timestamp = int(time.time())
        except Exception as error:
            logging.error(f'Сбой в работе программы:{error}')
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        else:
            send_message(bot, status_message)
        finally:
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()

