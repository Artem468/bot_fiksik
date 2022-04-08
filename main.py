import telebot
import wikipedia
from math import *
from translate import Translator
from config import TOKEN
import datetime
import requests
import dpath.util as dp
from cities import some_cities
from random import choice
import json
from config import *

bot = telebot.TeleBot(TOKEN)
list_of_languages = ['en', 'pl', 'fr', 'es', 'it', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'ru']


def translate_print(id, text):
    translator = Translator(from_lang='ru', to_lang=your_lang(id)[0])
    if your_lang(id)[0] == 'ru':
        bot.send_message(id, text)
    else:
        translation = translator.translate(text)
        bot.send_message(id, translation)


@bot.message_handler(commands=['start'])
def start(message):
    try:
        your = your_lang(message.chat.id)[0]
    except Exception:
        choose_lang(message.chat.id, 'ru')
    translate_print(message.chat.id, START_MESSAGE)


@bot.message_handler(commands=['help'])
def helping(message):
    translate_print(message.chat.id, HELP_MESSAGE)


def choose_lang(id, lang):
    with open('data/data_base.json', 'r+') as file:
        your_lang = {}
        data = json.loads(file.read())
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
            answer = f'{SELECT_LANG} {your_lang(message.chat.id)[0]}'
            translate_print(message.chat.id, answer)
        else:
            raise Exception
    except Exception:
        answer = f'{SELECT_LANGUAGE} {", ".join(list_of_languages)}'
        translate_print(message.chat.id, answer)


@bot.message_handler(commands=['search'], content_types=['text'])
def search_in_wikipedia(message):
    try:
        request_in_wiki = message.text.split()
        wikipedia.set_lang(your_lang(message.chat.id)[0])
        bot.send_message(message.chat.id, wikipedia.summary(' '.join(request_in_wiki[1:])))
    except Exception:
        try:
            answer = f'{SEARCH_MESSAGE_WRONG_WORD.capitalize()} {wikipedia.suggest(request_in_wiki[1])}'
            translate_print(message.chat.id, answer)
        except Exception:
            translate_print(message.chat.id, SEARCH_MESSAGE_WRONG_FORMAT)


@bot.message_handler(commands=['calc'], content_types=['text'])
def calculator(message):
    try:
        bot.send_message(message.chat.id, eval(str(message.text[5:])))
    except Exception:
        translate_print(message.chat.id, CALCULATOR_MESSAGE)


@bot.message_handler(commands=['translate'], content_types=['text'])
def tranlators(message):
    try:
        requests_in_translate = message.text.split()
        perevod = Translator(from_lang=requests_in_translate[1], to_lang=requests_in_translate[2])
        translation = perevod.translate((' '.join(requests_in_translate[3:])))
        bot.send_message(message.chat.id, translation)
    except Exception:
        translate_print(message.chat.id, TRANSLATE_MESSAGE)


@bot.message_handler(commands=['weather'], content_types=['text'])
def weather_now(message):
    try:
        requests_weather = message.text.split()
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={requests_weather[1]},"
                                f"{requests_weather[2]}&APPID=375945b5a4f84b8b46a5fd41b8d5f519",
                                params={'units': 'metric'})
        ans = response.content.decode('UTF-8')
        answer = ans.split(",")
        translator_for_cl = Translator(from_lang='en', to_lang=your_lang(message.chat.id)[0])
        clouds = translator_for_cl.translate(answer[4][15:-1])
        weather_atm = f'{clouds.capitalize()} \n{TEMPERATURE}: {answer[7][15:]} ' \
                      f'\n{HUMIDITY}: {answer[12][11:]} \n{SPEED_WIND}: {answer[16][16:]} '
        translate_print(message.chat.id, weather_atm)
    except Exception:
        translate_print(message.chat.id, WEATHER_MESSAGE)


list_of_timers = []


@bot.message_handler(commands=['set_timer'], content_types=['text'])
def timer(message):
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
                translate_print(message.chat.id, text)
                now = datetime.datetime.now()
                timer = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
                list_of_timers.append(str(now + timer)[:-7])
                while True:
                    if str(datetime.datetime.now())[:-7] in list_of_timers:
                        time = list_of_timers.index(str(datetime.datetime.now())[:-7])
                        translate_print(message.chat.id, TIMER_IS_OVER)
                        del list_of_timers[time]
                        break
    except Exception:
        translate_print(message.chat.id, TIMER_MESSAGE)


@bot.message_handler(commands='siuuu')
def siu(message):
    video = open('data/suiii.mp4', 'rb')
    bot.send_video(message.chat.id, video)


def update_city(id, city):
    with open('data/data_game_cities.json', 'r+') as file:
        your_city = {}
        your_city[str(id)] = []
        data = json.loads(file.read())
        try:
            for i in data[str(id)]:
                your_city[str(id)].append(i)
            your_city[str(id)].append(city)
        except Exception:
            your_city[str(id)].append(city)
        data_city = {**data, **your_city}
        print(data_city)

    with open('data/data_game_cities.json', 'w') as zapis:
        json.dump(data_city, zapis, indent=4)


def use_city(id):
    with open('data/data_game_cities.json') as file:
        try:
            dict = json.load(file)
            values = dict[str(id)]
            return values
        except Exception:
            return []


def del_cities(id):
    with open('data/data_game_cities.json', 'r+') as file:
        your_city = {}
        your_city[str(id)] = []
        data = json.loads(file.read())
        data_city = {**data, **your_city}
        print(data_city)

    with open('data/data_game_cities.json', 'w') as zapis:
        json.dump(data_city, zapis, indent=4)


@bot.message_handler(commands='cities')
def cities_game(message):
    try:
        city = []
        user_city = message.text.split()[1:]
        for word in user_city:
            city.append(word.capitalize())
        user_city = ' '.join(city)
        if use_city(message.chat.id) == []:
            last_mess = user_city[0].lower()
        else:
            last_mess = use_city(message.chat.id)[-1][-1]
        maybe_ans = []
        if user_city != 'Stop':
            if user_city in some_cities:
                if user_city in use_city(message.chat.id):
                    raise MemoryError
                if user_city[0].lower() != last_mess:
                    raise EOFError
                else:
                    for i in some_cities:
                        if i[0].lower() == user_city[-1]:
                            maybe_ans.append(i)
                    answer = choice(maybe_ans)
                    bot.send_message(message.chat.id, answer)
                    update_city(message.chat.id, user_city)
                    update_city(message.chat.id, answer)
                    translate_print(message.chat.id, ENTER_CITY)
            else:
                raise SyntaxError
        else:
            translate_print(message.chat.id, BYE_MESSAGE)
            del_cities(message.chat.id)
            return
    except SyntaxError:
        translate_print(message.chat.id, UNKNOWN_CITY)

    except MemoryError:
        translate_print(message.chat.id, CITY_USED)

    except EOFError:
        translate_print(message.chat.id, WRONG_LETTER)

    except IndexError:
        translate_print(message.chat.id, GAME_CITY_MESSAGE)


bot.polling(none_stop=True, interval=0)
