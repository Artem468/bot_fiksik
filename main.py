import telebot
import wikipedia
import math as m
from translate import Translator
from config import TOKEN
import datetime
import requests
from config import START_MESSAGE, HELP_MESSAGE, CALCULATOR_MESSAGE, WEATHER_MESSAGE, \
    TRANSLATE_MESSAGE, SEARCH_MESSAGE_WRONG_WORD, SEARCH_MESSAGE_WRONG_FORMAT, \
    SELECT_LANGUAGE, TEMPERATURE, HUMIDITY, SPEED_WIND

bot = telebot.TeleBot(TOKEN)
LANGUAGE = 'ru'
list_of_languages = ['en', 'ru', 'fr', 'es', 'it', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'pl']


@bot.message_handler(commands=['start'])
def start(message):
    global LANGUAGE
    translator = Translator(from_lang='ru', to_lang=LANGUAGE)
    translation = translator.translate((START_MESSAGE).lower())
    bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['help'])
def helping(message):
    global LANGUAGE
    translator = Translator(from_lang='ru', to_lang=LANGUAGE)
    translation = translator.translate((HELP_MESSAGE).lower())
    bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['language'], content_types=['text'])
def select_language(message):
    global LANGUAGE, list_of_languages
    try:
        request_language = message.text.split()[1]
        if request_language in list_of_languages:
            LANGUAGE = request_language
        else:
            raise Exception
    except Exception:
        translator = Translator(from_lang='ru', to_lang=LANGUAGE)
        translation = translator.translate((SELECT_LANGUAGE).lower())
        bot.send_message(message.chat.id, f'{translation.capitalize()} {", ".join(list_of_languages)}')


@bot.message_handler(commands=['search'], content_types=['text'])
def search_in_wikipedia(message):
    global LANGUAGE
    try:
        request_in_wiki = message.text.split()
        wikipedia.set_lang(LANGUAGE)
        bot.send_message(message.chat.id, wikipedia.summary(request_in_wiki[1]))
    except Exception:
        try:
            translator = Translator(from_lang='ru', to_lang=LANGUAGE)
            translation = translator.translate((SEARCH_MESSAGE_WRONG_WORD).lower())
            bot.send_message(message.chat.id, f'{translation.capitalize()} {wikipedia.suggest(request_in_wiki[1])}')
        except Exception:
            translator = Translator(from_lang='ru', to_lang=LANGUAGE)
            translation = translator.translate((SEARCH_MESSAGE_WRONG_FORMAT).lower())
            bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['calc'], content_types=['text'])
def calculator(message):
    global LANGUAGE
    try:
        bot.send_message(message.chat.id, eval(str(message.text[5:])))
    except Exception:
        translator = Translator(from_lang='ru', to_lang=LANGUAGE)
        translation = translator.translate((CALCULATOR_MESSAGE).lower())
        bot.send_message(message.chat.id, translation)


@bot.message_handler(commands=['translate'], content_types=['text'])
def tranlators(message):
    try:
        requests_in_translate = message.text.split()
        translator = Translator(from_lang=requests_in_translate[1], to_lang=requests_in_translate[2])
        translation = translator.translate((' '.join(requests_in_translate[3:])).lower())
        bot.send_message(message.chat.id, translation)
    except Exception:
        translator = Translator(from_lang='ru', to_lang=LANGUAGE)
        translation = translator.translate((TRANSLATE_MESSAGE).lower())
        bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['weather'], content_types=['text'])
def weather_now(message):
    global LANGUAGE
    try:
        requests_weather = message.text.split()
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={requests_weather[1]},"
                                f"{requests_weather[2]}&APPID=375945b5a4f84b8b46a5fd41b8d5f519",
                                params={'units': 'metric'})
        ans = response.content.decode('UTF-8')
        answer = ans.split(",")
        translator = Translator(from_lang='ru', to_lang=LANGUAGE)
        clouds = translator.translate(answer[4][15:-1].lower())
        temp = translator.translate(TEMPERATURE)
        hum = translator.translate(HUMIDITY)
        sp_wind = translator.translate(SPEED_WIND)
        weather_atm = f'{clouds} \n{temp}: {answer[7][15:]} \n{hum}: {answer[12][11:]} \n{sp_wind}: {answer[16][16:]}'
        bot.send_message(message.chat.id, weather_atm)
    except Exception:
        translator = Translator(from_lang='ru', to_lang=LANGUAGE)
        translation = translator.translate(WEATHER_MESSAGE)
        bot.send_message(message.chat.id, translation)


list_of_timers = []


@bot.message_handler(commands=['create_timer'], content_types=['text'])
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
