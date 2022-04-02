import telebot
import wikipedia
import math as m
from translate import Translator
from config import TOKEN
import datetime
import requests
import dpath.util as dp
import json
from config import START_MESSAGE, HELP_MESSAGE, CALCULATOR_MESSAGE, WEATHER_MESSAGE, \
    TRANSLATE_MESSAGE, SEARCH_MESSAGE_WRONG_WORD, SEARCH_MESSAGE_WRONG_FORMAT, \
    SELECT_LANGUAGE, TEMPERATURE, HUMIDITY, SPEED_WIND, TIMER_IS_OVER, TIMER_MESSAGE, SELECT_LANG


bot = telebot.TeleBot(TOKEN)
list_of_languages = ['en', 'ru', 'fr', 'es', 'it', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'pl']


@bot.message_handler(commands=['start'])
def start(message):
    try:
        your = your_lang(message.chat.id)[0]
    except Exception:
        choose_lang(message.chat.id, 'ru')
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    if your_lang(message.chat.id)[0] == 'ru':
        bot.send_message(message.chat.id, START_MESSAGE)
    else:
        translation = translator.translate(START_MESSAGE)
        bot.send_message(message.chat.id, translation)


@bot.message_handler(commands=['help'])
def helping(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    if your_lang(message.chat.id)[0] == 'ru':
        bot.send_message(message.chat.id, HELP_MESSAGE)
    else:
        translation = translator.translate(HELP_MESSAGE)
        bot.send_message(message.chat.id, translation)


def choose_lang(id, lang):
    with open('data/data_base.json', 'r+') as file:
        your_lang = {}
        data = json.loads(file.read())
        print(type(file))
        your_lang[str(id)] = lang
        data_lang = {**data, **your_lang}
        print(data_lang)

    with open('data/data_base.json', 'w') as zapis:
        json.dump(data_lang, zapis, indent=4)


def your_lang(id):
    with open('data/data_base.json') as file:
        dict = json.load(file)
        values = dp.values(dict, str(id))
        return values


@bot.message_handler(commands=['language'], content_types=['text'])
def select_language(message):
    global list_of_languages
    try:
        request_language = message.text.split()[1]
        if request_language in list_of_languages:
            choose_lang(message.chat.id, request_language)

            if your_lang(message.chat.id)[0] == 'ru':
                bot.send_message(message.chat.id, f'{SELECT_LANG} {your_lang(message.chat.id)[0]}')
            else:
                translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
                translation = translator.translate(SELECT_LANG)
                bot.send_message(message.chat.id, f'{translation.capitalize()} {your_lang(message.chat.id)[0]}')
        else:
            raise Exception
    except Exception:
        if your_lang(message.chat.id)[0] == 'ru':
            bot.send_message(message.chat.id, f'{SELECT_LANGUAGE} {", ".join(list_of_languages)}')
        else:
            translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
            translation = translator.translate(SELECT_LANGUAGE)
            bot.send_message(message.chat.id, f'{translation} {", ".join(list_of_languages)}')


@bot.message_handler(commands=['search'], content_types=['text'])
def search_in_wikipedia(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    try:
        request_in_wiki = message.text.split()
        wikipedia.set_lang(your_lang(message.chat.id)[0])
        bot.send_message(message.chat.id, wikipedia.summary(' '.join(request_in_wiki[1:])))
    except Exception:
        try:
            if your_lang(message.chat.id)[0] == 'ru':
                bot.send_message(message.chat.id, f'{SEARCH_MESSAGE_WRONG_WORD.capitalize()} '
                                                  f'{wikipedia.suggest(request_in_wiki[1])}')
            else:
                translation = translator.translate((SEARCH_MESSAGE_WRONG_WORD))
                bot.send_message(message.chat.id, f'{translation.capitalize()} '
                                                  f'{wikipedia.suggest(request_in_wiki[1])}')
        except Exception:
            if your_lang(message.chat.id)[0] == 'ru':
                bot.send_message(message.chat.id, SEARCH_MESSAGE_WRONG_FORMAT.capitalize())
            else:
                translation = translator.translate(SEARCH_MESSAGE_WRONG_FORMAT)
                bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['calc'], content_types=['text'])
def calculator(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    try:
        bot.send_message(message.chat.id, eval(str(message.text[5:])))
    except Exception:
        if your_lang(message.chat.id)[0] == 'ru':
            bot.send_message(message.chat.id, CALCULATOR_MESSAGE)
        else:
            translation = translator.translate(CALCULATOR_MESSAGE)
            bot.send_message(message.chat.id, translation)


@bot.message_handler(commands=['translate'], content_types=['text'])
def tranlators(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    try:
        requests_in_translate = message.text.split()
        perevod = Translator(from_lang=requests_in_translate[1], to_lang=requests_in_translate[2])
        translation = perevod.translate((' '.join(requests_in_translate[3:])))
        bot.send_message(message.chat.id, translation)
    except Exception:
        if your_lang(message.chat.id)[0] == 'ru':
            bot.send_message(message.chat.id, TRANSLATE_MESSAGE.capitalize())
        else:
            translation = translator.translate(TRANSLATE_MESSAGE)
            bot.send_message(message.chat.id, translation.capitalize())


@bot.message_handler(commands=['weather'], content_types=['text'])
def weather_now(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    try:
        requests_weather = message.text.split()
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={requests_weather[1]},"
                                f"{requests_weather[2]}&APPID=375945b5a4f84b8b46a5fd41b8d5f519",
                                params={'units': 'metric'})
        ans = response.content.decode('UTF-8')
        answer = ans.split(",")
        translator_for_cl = Translator(from_lang='en', to_lang=your_lang(message.chat.id)[0])
        clouds = translator_for_cl.translate(answer[4][15:-1])
        if your_lang(message.chat.id)[0] == 'ru':
            weather_atm = f'{clouds.capitalize()} \n{TEMPERATURE}: {answer[7][15:]} ' \
                          f'\n{HUMIDITY}: {answer[12][11:]} \n{SPEED_WIND}: {answer[16][16:]} '
        else:
            temp = translator.translate(TEMPERATURE)
            hum = translator.translate(HUMIDITY)
            sp_wind = translator.translate(SPEED_WIND)
            weather_atm = f'{clouds.capitalize()} \n{temp}: {answer[7][15:]}' \
                          f' \n{hum}: {answer[12][11:]} \n{sp_wind}: {answer[16][16:]} '
        bot.send_message(message.chat.id, weather_atm)
    except Exception:
        if your_lang(message.chat.id)[0] == 'ru':
            bot.send_message(message.chat.id, WEATHER_MESSAGE)
        else:
            translation = translator.translate(WEATHER_MESSAGE)
            bot.send_message(message.chat.id, translation)


list_of_timers = []


@bot.message_handler(commands=['set_timer'], content_types=['text'])
def timer(message):
    translator = Translator(from_lang='ru', to_lang=your_lang(message.chat.id)[0])
    try:
        hours = 0
        minutes = 0
        seconds = 0
        requests_in_timer = message.text.split()
        if len(requests_in_timer) == 1:
            raise Exception
        else:
            for arg in requests_in_timer:
                if 'h' in arg:
                    hours = int(arg[:-1])
                if 'min' in arg:
                    minutes = int(arg[:-3])
                if 'sec' in arg:
                    seconds = int(arg[:-3])
            if hours < 0 or minutes < 0 or seconds < 0:
                raise Exception
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
                if your_lang(message.chat.id)[0] == 'ru':
                    bot.send_message(message.chat.id, text)
                else:
                    translation = translator.translate(text)
                    bot.send_message(message.chat.id, translation)
                now = datetime.datetime.now()
                timer = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
                list_of_timers.append(str(now + timer)[:-7])
                if your_lang(message.chat.id)[0] == 'ru':
                    translation = TIMER_IS_OVER
                else:
                    translation = translator.translate(TIMER_IS_OVER)
                while True:
                    if str(datetime.datetime.now())[:-7] in list_of_timers:
                        time = list_of_timers.index(str(datetime.datetime.now())[:-7])
                        bot.send_message(message.chat.id, translation)
                        del list_of_timers[time]
                        break
    except Exception:
        if your_lang(message.chat.id)[0] == 'ru':
            bot.send_message(message.chat.id, TIMER_MESSAGE)
        else:
            translation = translator.translate(TIMER_MESSAGE)
            bot.send_message(message.chat.id, translation)


@bot.message_handler(commands='siuuu')
def siu(message):
    video = open('data/suiii.mp4', 'rb')
    bot.send_video(message.chat.id, video)


bot.polling(none_stop=True, interval=0)
