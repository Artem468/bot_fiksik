import telebot
import wikipedia
from math import *
from translate import Translator
import datetime
import requests
import dpath.util as dp
from cities import some_cities
from random import choice, randint, shuffle
import json
from config import *
import easyocr
import os
import matplotlib.pyplot as plt
import numpy as np


bot = telebot.TeleBot(TOKEN)
list_of_languages = ['en', 'pl', 'fr', 'es', 'it', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'ru']
list_of_timers = []


def translate_print(id, text):
    try:
        translator = Translator(from_lang='ru', to_lang=your_lang(id)[0])
        if your_lang(id)[0] == 'ru':
            bot.send_message(id, text)
        else:
            translation = translator.translate(text)
            bot.send_message(id, translation)
    except Exception as e:
        bot.send_message(id, e)


def id_user(id, name):
    with open('data/id_username.json', 'r+') as file:
        your_indif = {}
        data = json.loads(file.read())
        your_indif[str(id)] = name
        data_indif = {**data, **your_indif}

    with open('data/id_username.json', 'w') as zapis:
        json.dump(data_indif, zapis, indent=4)


@bot.message_handler(commands=['start'])
def start(message):
    try:
        your_lang(message.chat.id)[0]
    except Exception:
        choose_lang(message.chat.id, 'ru')
        id_user(message.chat.id, message.chat.username)

    bot.set_my_commands([
        telebot.types.BotCommand("/start", "main menu"),
        telebot.types.BotCommand("/help", "about bot"),
        telebot.types.BotCommand("/language", "change language"),
        telebot.types.BotCommand("/search", "search in wikipedia"),
        telebot.types.BotCommand("/translate", "for translate some text"),
        telebot.types.BotCommand("/weather", "show weather now"),
        telebot.types.BotCommand("/random", "random number"),
        telebot.types.BotCommand("/calc", "for calculate"),
        telebot.types.BotCommand("/cities", "the city game"),
        telebot.types.BotCommand("/set_timer", "create a timer [beta]"),
        telebot.types.BotCommand("/quiz", "the quiz"),
        telebot.types.BotCommand("/res_quiz", "result from quiz"),
        telebot.types.BotCommand("/graph", "create graph")
    ])
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/help', '/language', '/search', '/res_quiz')
    keyboard.row('/translate', '/weather', '/set_timer', '/quiz')
    keyboard.row('/random', '/cities', '/calc', '/graph')
    bot.send_photo(message.chat.id, photo=open(r'data/fiksik.png', 'rb'), reply_markup=keyboard)
    translate_print(message.chat.id, START_MESSAGE)


@bot.message_handler(commands=['help'])
def helping(message):
    translate_print(message.chat.id, HELP_MESSAGE)


def choose_lang(id, lang):
    with open('data/id_lang.json', 'r+') as file:
        user_lang = {}
        data = json.loads(file.read())
        user_lang[str(id)] = lang
        data_lang = {**data, **user_lang}

    with open('data/id_lang.json', 'w') as zapis:
        json.dump(data_lang, zapis, indent=4)


def your_lang(id):
    with open('data/id_lang.json') as file:
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
        requests_weather = message.text.split()[1:]
        if len(requests_weather) <= 1:
            raise Exception
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={' '.join(requests_weather[0:-1])},"
                                f"{requests_weather[-1]}&APPID=375945b5a4f84b8b46a5fd41b8d5f519",
                                params={'units': 'metric'})

        ans = json.loads(response.content.decode('utf-8'))
        translator_for_cl = Translator(from_lang='en', to_lang=your_lang(message.chat.id)[0])
        clouds = translator_for_cl.translate(ans['weather'][0]['description'])
        weather_atm = f'{clouds.capitalize()} \n' \
                      f'{TEMPERATURE}: {ans["main"]["temp"]} \n' \
                      f'{HUMIDITY}: {ans["main"]["humidity"]} \n' \
                      f'{SPEED_WIND}: {ans["wind"]["speed"]}'
        translate_print(message.chat.id, weather_atm)
    except Exception:
        translate_print(message.chat.id, WEATHER_MESSAGE)


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
                text = '????????????! ?????????????? ?????????? '
                if hours:
                    if hours == 1:
                        text += f'{str(hours)} ?????? '
                    elif 2 <= hours <= 4:
                        text += f'{str(hours)} ???????? '
                    elif hours >= 5:
                        text += f'{str(hours)} ?????????? '
                if minutes:
                    if minutes == 1:
                        text += f'{str(minutes)} ???????????? '
                    if 2 <= minutes <= 4:
                        text += f'{str(minutes)} ???????????? '
                    if minutes >= 5:
                        text += f'{str(minutes)} ?????????? '
                if seconds:
                    if seconds == 1:
                        text += f'{str(seconds)} ??????????????'
                    if 2 <= seconds <= 4:
                        text += f'{str(seconds)} ??????????????'
                    if seconds >= 5:
                        text += f'{str(seconds)} ????????????'
                text.strip()
                if your_lang(message.chat.id)[0] == 'en':
                    gif = open("data/I'll be back.gif", 'rb')
                    bot.send_video(message.chat.id, gif)
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


# ?????????????????? ???? ??????????????  :D
@bot.message_handler(commands='siuuu')
def siu(message):
    video = open('data/suiii.mp4', 'rb')
    bot.send_video(message.chat.id, video)


# Adds city to db
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

    with open('data/data_game_cities.json', 'w') as zapis:
        json.dump(data_city, zapis, indent=4)


# Check used cities
def use_city(id):
    with open('data/data_game_cities.json') as file:
        try:
            dict = json.load(file)
            values = dict[str(id)]
            return values
        except Exception:
            return []


# Deletes used cities
def del_cities(id):
    with open('data/data_game_cities.json', 'r+') as file:
        your_city = {}
        your_city[str(id)] = []
        data = json.loads(file.read())
        data_city = {**data, **your_city}

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
                    if len(maybe_ans) == 0:
                        translate_print(message.chat.id, '???? ??????????????!')
                        del_cities(message.chat.id)
                        return
                    else:
                        answer = choice(maybe_ans)
                        bot.send_message(message.chat.id, answer)
                        update_city(message.chat.id, user_city)
                        update_city(message.chat.id, answer)
                        translate_print(message.chat.id, ENTER_CITY)
            else:
                raise SyntaxError
        else:
            translate_print(message.chat.id, f"{BYE_MESSAGE} ?????????????????? ???????????? - {len(use_city(message.chat.id)) // 2} ??????????????")
            del_cities(message.chat.id)
            return
    except SyntaxError:
        translate_print(message.chat.id, UNKNOW_CITY)

    except MemoryError:
        translate_print(message.chat.id, CITY_USED)

    except EOFError:
        translate_print(message.chat.id, WRONG_LETTER)

    except IndexError:
        translate_print(message.chat.id, GAME_CITY_MESSAGE)


@bot.message_handler(commands='random')
def randomaizer(message):
    try:
        if '???' in message.text.split()[1]:
            fromm = message.text.split()[1][:message.text.split()[1].rfind('???')]
            to = '-' + message.text.split()[1][message.text.split()[1].rfind('???'):][1:]
        else:
            fromm, to = (message.text.split()[1:])[0].split('-')
        bot.send_message(message.chat.id, str(randint(int(fromm), int(to))))
    except Exception:
        translate_print(message.chat.id, RANDOM_MESSAGE)


# Sends you text from the photo, you've sent
# !!!WARNING!!! It takes some time. It depends on strength of your CPU
@bot.message_handler(content_types=['photo'])
def text_from_image(message):
    f_id = message.photo[-1].file_id
    file_info = bot.get_file(f_id)
    down_file = bot.download_file(file_info.file_path)
    with open(f'images/{message.chat.id}.jpg', 'wb') as file:
        file.write(down_file)
    reader = easyocr.Reader(['en', 'ru'], gpu=True)
    result = reader.readtext(f'images/{message.chat.id}.jpg', detail=0, paragraph=True)
    bot.send_message(message.chat.id, result)
    os.remove(f'images/{message.chat.id}.jpg')


# Writes right answers
def write_true_ans(id, ans):
    with open('data/quizs.json', 'r+') as file:
        true_answer = {}
        data = json.loads(file.read())
        true_answer[str(id)] = ans
        data_ans = {**data, **true_answer}

    with open('data/quizs.json', 'w') as zapis:
        json.dump(data_ans, zapis, indent=4)


# Checks if the answer is right
def read_true_ans(id):
    with open('data/quizs.json') as file:
        dict = json.load(file)
        values = dp.values(dict, str(id))
        return values


# Main function of quiz
@bot.message_handler(commands='quiz')
def quiz_process(message):
    try:
        may_be_ans = []
        question_and_three_ans = requests.get('http://jservice.io/api/random?count=3')
        may_be_ans.append(question_and_three_ans.json()[0]["answer"])
        may_be_ans.append(question_and_three_ans.json()[1]["answer"])
        may_be_ans.append(question_and_three_ans.json()[2]["answer"])
        shuffle(may_be_ans)
        bot.send_poll(message.chat.id, question_and_three_ans.json()[0]["question"], options=may_be_ans,
                      type='quiz', correct_option_id=may_be_ans.index(question_and_three_ans.json()[0]["answer"]),
                      is_anonymous=False)
        write_true_ans(message.chat.id, may_be_ans.index(question_and_three_ans.json()[0]["answer"]))
    except Exception as d:
        bot.send_message(message.chat.id, str(d))


# + scores, if it's right and - scores, if it's wrong
@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    if pollAnswer.to_dict()['option_ids'] == read_true_ans(pollAnswer.to_dict()['user']['id']):
        write_score(pollAnswer.to_dict()['user']['id'], 1)
    else:
        write_score(pollAnswer.to_dict()['user']['id'], -1)


# Gives scores
def write_score(id, mark):
    with open('data/score_users.json', 'r+') as file:
        score = {}
        data = json.load(file)
        values = dp.values(data, str(id))
        if len(values) == 0:
            values.append(0)
            values[0] += int(mark)
        else:
            values[0] += int(mark)
        if values[0] < 0:
            values[0] = 0
        score[str(id)] = values[0]
        data_score = {**data, **score}

    with open('data/score_users.json', 'w') as zapis:
        json.dump(data_score, zapis, indent=4)


# Sends scores
@bot.message_handler(commands='res_quiz')
def read_score(message):
    try:
        with open('data/score_users.json') as file:
            dict = json.load(file)
            sorted_dict = {}
            sorted_keys = sorted(dict, key=dict.get, reverse=True)
            for w in sorted_keys:
                sorted_dict[w] = dict[w]

            if len(sorted_dict) > 5:
                number = 5
            else:
                number = len(sorted_dict)

        with open('data/id_username.json') as file:
            id_and_name = json.load(file)
            stroka = ''
            list_of_emoji = ['\U0001F60E', '\U0001F973', '\U0001F929', '\U0001F9D0', '\U0001F92A']
            for i in range(1, number + 1):
                stroka += f'{i}. {dp.values(id_and_name, list(sorted_dict.keys())[i - 1])[0]}'\
                          f' - {dp.values(sorted_dict, str(list(sorted_dict.keys())[i - 1]))[0]} {list_of_emoji[i - 1]} \n'
            bot.send_message(message.chat.id, f"\u203C\uFE0F your score - "
                                              f" {dp.values(sorted_dict, str(message.chat.id))[0]} \u203C\uFE0F \n \n{stroka}")
    except Exception:
        translate_print(message.chat.id, QUIZ_MESSAGE)


# Gives scores to each player
@bot.message_handler(commands='give_score')
def giving_score(message):
    try:
        if message.chat.id in [932288986, 1985628010]:
            person, score = message.text.split()[1:]
            write_score(person, score)
            translate_print(message.chat.id, '???????????? ??????????????')
    except Exception:
        translate_print(message.chat.id, '?? ?????? ???? ???????????????????? ???????? ?????? ?????????????????????????? ???????????? ?????????????? \n'
                                         ' ?????? ?????? ???? ?????????? ???? ??????')


@bot.message_handler(commands='my_id')
def myid(message):
    bot.send_message(message.chat.id, message.chat.id)


# Sends you a graph
@bot.message_handler(commands='graph')
def graphic(message):
    try:

        fig = plt.figure()
        param = message.text.split()[1:]
        func = param[0]
        x_min = int(param[1])
        x_max = int(param[2])
        x_x = [i for i in range(x_min, x_max + 1, 1)]
        y_y = []
        for x in x_x:
            func.replace("x", str(x))
            y_y.append(eval(func))

        plt.plot(x_x, y_y, 'r')
        fig.savefig(f'images/{message.chat.id}.png')
        place = open(f'images/{message.chat.id}.png', 'rb')
        bot.send_photo(message.chat.id, place)
        place.close()
        os.remove(f'images/{message.chat.id}.png')
    except Exception:
        bot.send_message(message.chat.id, GRAPH_MESSAGE)


bot.polling(none_stop=True, interval=0)
