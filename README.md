# homework_bot
telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус проверки домашней работы.

## Особенности бота:
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет пользователю соответствующее уведомление в Telegram;
- логирует свою работу и сообщает пользователю о важных проблемах сообщением в Telegram.


## Используемые технологии:
- Python
- Telegram
- Bot API
- JSON

## Пример ответов API:
`{
"homeworks":[
{
"id":124,
"status":"rejected",
"homework_name":"username__hw_python_oop.zip",
"reviewer_comment":"Код не по PEP8, нужно исправить",
"date_updated":"2020-02-13T16:42:47Z",
"lesson_name":"Итоговый проект"
},
{
"id":123,
"status":"approved",
"homework_name":"username__hw_test.zip",
"reviewer_comment":"Всё нравится",
"date_updated":"2020-02-11T14:40:57Z",
"lesson_name":"Тестовый проект"
},
...
],
"current_date":1581604970
}`




