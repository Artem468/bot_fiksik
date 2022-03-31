import telebot
import wikipedia
import math as m
from translate import Translator
from config import TOKEN
import datetime
import requests
from config import START_MESSAGE

bot = telebot.TeleBot(TOKEN)
LANGUAGE = 'ru'
LIST_OF_LANGUAGES = ['en', 'ru', 'fr', 'es', 'it', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'pl']

LOCATION = 'Kaliningrad ru'


@bot.message_handler(commands=['start'])
def start(message):
    global LANGUAGE
    translator = Translator(from_lang='ru', to_lang=LANGUAGE)
    translation = translator.translate((START_MESSAGE))
    bot.send_message(message.chat.id, translation)


@bot.message_handler(commands=['help'])
def helping(message):
    bot.send_message(message.chat.id, 'Я могу: '
                                      '\n   установить язык (функция /language)'
                                      '\n   искать в википедии (функция /search)'
                                      '\n   выполнять математические действия (функция /calc)'
                                      '\n   переводить тексты (функция /translate)'
                                      '\n   показывать погоду (функция /weather)'
                                      '\n   создавать таймер (функция /timer)')


@bot.message_handler(commands=['location'], content_types=['text'])
def select_location(message):
    global LOCATION
    try:
        request_location = message.text.split()
        if len(request_location) == 3:
            if request_location[2] in LIST_OF_LANGUAGES:
                LOCATION = ' '.join(request_location[1:])
                bot.send_message(message.chat.id, f'Местоположение сменено на <{LOCATION}>')
            else:
                raise Exception
        else:
            raise SyntaxError
    except SyntaxError:
        bot.send_message(message.chat.id, f'Не хватает данных для запроса. \n'
                                          f'Пример ввода: /location Moscow ru'
                                          f'\nДоступные сокращения стран: {", ".join(LIST_OF_LANGUAGES)}')
    except Exception:
        bot.send_message(message.chat.id, f'Извините, этой локации нет в нашей базе. \n'
                                          f'Пример ввода: /location Moscow ru'
                                          f'\n Доступные сокращения стран: {", ".join(LIST_OF_LANGUAGES)}')

@bot.message_handler(commands=['language'], content_types=['text'])
def select_language(message):
    global LANGUAGE, LIST_OF_LANGUAGES
    try:
        request_language = message.text.split()[1]
        if request_language in LIST_OF_LANGUAGES:
            LANGUAGE = request_language
            translator = Translator(from_lang='ru', to_lang=LANGUAGE)
            translation = translator.translate(f'Язык сменён на <{LANGUAGE}>')
            bot.send_message(message.chat.id, translation)
        else:
            raise Exception
    except Exception:
        bot.send_message(message.chat.id, f'Извините, этого языка нет в нашей базе. \n'
                                          f'Пример ввода: /language ru'
                                          f'\n Доступные языки {", ".join(LIST_OF_LANGUAGES)}')


@bot.message_handler(commands=['search'], content_types=['text'])
def search_in_wikipedia(message):
    try:
        request_in_wiki = message.text.split()
        wikipedia.set_lang(request_in_wiki[1])
        bot.send_message(message.chat.id, wikipedia.summary(request_in_wiki[2]))
    except Exception:
        try:
            bot.send_message(message.chat.id,
                             f'Убедитесь в корректности запроса и запрашиваемого слова.'
                             f'\nПример запроса: /search ru телеграмм'
                             f'\nИспользуются стандартные сокращения языков'
                             f' на английском языке, например:\n'
                             f'en - английский\n'
                             f'ru - русский\n'
                             f'и так далее.'
                             f'\nВозможно вы имели в виду '
                             f'{wikipedia.suggest(request_in_wiki[2])}')
        except Exception:
            bot.send_message(message.chat.id, f'Неккоректный формат ввода.'
                                              f'\nПример запроса: /search ru телеграм')


@bot.message_handler(commands=['calc'], content_types=['text'])
def calculator(message):
    try:
        bot.send_message(message.chat.id, eval(str(message.text[5:])))
    except Exception:
        bot.send_message(message.chat.id, 'Проверьте правильность написания примера.'
                                          '\nДоступные математические функции можно'
                                          ' узнать по ссылке: https://pythonworld.ru/moduli/modul-math.html')


@bot.message_handler(commands=['translate'], content_types=['text'])
def tranlators(message):
    try:
        requests_in_translate = message.text.split()
        translator = Translator(from_lang=requests_in_translate[1], to_lang=requests_in_translate[2])
        translation = translator.translate((' '.join(requests_in_translate[3:])).lower())
        bot.send_message(message.chat.id, translation)
    except Exception:
        bot.send_message(message.chat.id, 'Проверьте правильность написания.    '
                                          'Пример ввода: /translate en ru telegram.'
                                          '\nИспользуются стандартные сокращения языков'
                                          ' на английском языке, например:\n'
                                          'en - английский\n'
                                          'ru - русский\n'
                                          'и так далее.')


@bot.message_handler(commands=['weather'], content_types=['text'])
def weather_now(message):
    try:
        requests_weather = message.text.split()
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={requests_weather[1]},"
                                f"{requests_weather[2]}&APPID=375945b5a4f84b8b46a5fd41b8d5f519",
                                params={'units': 'metric'})
        ans = response.content.decode('UTF-8')
        answer = ans.split(",")
        translator = Translator(to_lang=LANGUAGE)
        translation = translator.translate(answer[4][15:-1].lower())
        bot.send_message(message.chat.id, f'{translation.capitalize()} \nТемпература: {answer[7][15:]}'
                                          f' \nВлажность: {answer[12][11:]} \nСкорость ветра: {answer[16][16:]}')
    except Exception:
        bot.send_message(message.chat.id, 'Проверьте корректность написания \nПример ввода: '
                                          '/weather Moscow ru')


list_of_timers = []


@bot.message_handler(commands=['timer'], content_types=['text'])
def timer(message):
    try:
        hours = 0
        minutes = 0
        seconds = 0
        requests_in_timer = message.text.split()
        if len(requests_in_timer) == 1:
            bot.send_message(message.chat.id, 'Пример запроса: /timer <часы>h <минуты>min <секунды>sec')
        else:
            for arg in requests_in_timer:
                if 'h' in arg:
                    hours = int(arg[:-1])
                if 'min' in arg:
                    minutes = int(arg[:-3])
                if 'sec' in arg:
                    seconds = int(arg[:-3])
            if hours < 0 or minutes < 0 or seconds < 0:
                bot.send_message(message.chat.id, 'Извини, я не умею возвращать время назад.')
            if hours == 0 and minutes == 0 and seconds == 0:
                raise Exception
            else:
                text = 'Хорошо! Вернусь через '
                if hours:
                    if hours == 1:
                        text += f'{str(hours)} час '
                    elif 2 <= hours <= 4:
                        text += f'{str(hours)} часа '
                    elif hours >= 5:
                        text += f'{str(hours)} часов '
                if minutes:
                    if minutes == 1:
                        text += f'{str(minutes)} минуту '
                    if 2 <= minutes <= 4:
                        text += f'{str(minutes)} минуты '
                    if minutes >= 5:
                        text += f'{str(minutes)} минут '
                if seconds:
                    if seconds == 1:
                        text += f'{str(seconds)} секунду'
                    if 2 <= seconds <= 4:
                        text += f'{str(seconds)} секунды'
                    if seconds >= 5:
                        text += f'{str(seconds)} секунд'
                text.strip()
                bot.send_message(message.chat.id, text)
                now = datetime.datetime.now()
                timer = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
                list_of_timers.append(str(now + timer)[:-7])
                while True:
                    if str(datetime.datetime.now())[:-7] in list_of_timers:
                        time = list_of_timers.index(str(datetime.datetime.now())[:-7])
                        bot.send_message(message.chat.id, 'Время таймера вышло :D')
                        del list_of_timers[time]
                        break
    except Exception:
        bot.send_message(message.chat.id, f'Неккоректный формат ввода.'
                                          f'\nПример запроса: /timer <часы>h <минуты>min <секунды>sec')


bot.polling(none_stop=True, interval=0)