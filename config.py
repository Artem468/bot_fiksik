TOKEN = 'YOUR TOKEN'

START_MESSAGE = 'Привет, я бот-фиксик! Для работы со мной используй функции, описанные в - /help. \n' \
                'Для смены языка напишите /language " язык в сокращенной форме " '

HELP_MESSAGE = 'Я могу: \n   искать в википедии (функция /search) ' \
               '\n   выполнять математические действия (функция /calc)' \
               '\n   переводить тексты (функция /translate)' \
               '\n   показывать погоду (функция /weather)' \
               '\n   создавать таймер (функция /set_timer)'

CALCULATOR_MESSAGE = 'Проверьте правильность написания примера.' \
                    '\nДоступные математические функции можно' \
                    ' узнать по ссылке: https://pythonworld.ru/moduli/modul-math.html'

TRANSLATE_MESSAGE = 'Проверьте правильность написания.    ' \
                    'Пример ввода: /translate en ru telegram. \n' \
                    'Используются стандартные сокращения языков' \
                    'на английском языке, например: \n' \
                    'en - английский \n' \
                    'ru - русский \n' \
                    'и так далее.'

SEARCH_MESSAGE_WRONG_WORD = 'Убедитесь в корректности запроса и запрашиваемого слова. \n' \
                            'Пример запроса: /search ru телеграмм \n'\
                            'Используются стандартные сокращения языков' \
                            ' на английском языке, например: \n' \
                            'en - английский \n' \
                            'ru - русский \n' \
                            'и так далее. \n' \
                            'Возможно вы имели в виду:'

SEARCH_MESSAGE_WRONG_FORMAT = 'Неккоректный формат ввода. \n' \
                              'Пример запроса: /search telegram'

SELECT_LANGUAGE = 'Извините, этого языка нет в нашей базе. \n' \
                  'Пример ввода: /language ru \n' \
                  'Доступные языки:'

TEMPERATURE = 'Температура'
HUMIDITY = 'Влажность воздуха'
SPEED_WIND = 'Скорость ветра'

WEATHER_MESSAGE = 'Проверьте правильность написания \n' \
                  'Пример ввода: /weather Moscow ru'

TIMER_IS_OVER = 'Время таймера вышло :D'

TIMER_MESSAGE = 'Неккоректный формат ввода. \n' \
                'Пример запроса: /timer {часы}h {минуты}min {секунды}sec'

SELECT_LANG = 'Язык изменился на:'
