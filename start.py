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


bot = telebot.TeleBot(TOKEN)
list_of_languages = ['en', 'pl', 'fr', 'es', 'it', 'zh', 'ja', 'ko', 'ar', 'hi', 'pt', 'de', 'ru']
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
        print(data_indif)

    with open('data/id_username.json', 'w') as zapis:
        json.dump(data_indif, zapis, indent=4)


@bot.message_handler(commands=['start'])
def start(message):
    try:
        your = your_lang(message.chat.id)[0]
    except Exception:
        choose_lang(message.chat.id, 'ru')
        id_user(message.chat.id, message.chat.username)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/help', '/language', '/search', '/res_quiz')
    keyboard.row('/translate', '/weather', '/set_timer', '/quiz')
    keyboard.row('/random', '/cities', '/calc',)
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
        print(data_lang)

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
                        translate_print(message.chat.id, 'ты победил!')
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
            translate_print(message.chat.id, BYE_MESSAGE)
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
        fromm, to = (message.text.split()[1:])[0].split('-')
        bot.send_message(message.chat.id, str(randint(int(fromm), int(to))))
    except Exception:
        translate_print(message.chat.id, RANDOM_MESSAGE)


@bot.message_handler(content_types=['photo'])
def text_from_image(message):
    f_id = message.photo[-1].file_id
    file_info = bot.get_file(f_id)
    down_file = bot.download_file(file_info.file_path)
    with open(f'images/{message.chat.id}.jpg', 'wb') as file:
        file.write(down_file)
    reader = easyocr.Reader(list_of_languages)
    result = reader.readtext(f'images/{message.chat.id}.jpg', detail=0, paragraph=True)
    bot.send_message(message.chat.id, result)
    os.remove(f'images/{message.chat.id}.jpg')


def write_true_ans(id, ans):
    with open('data/quizs.json', 'r+') as file:
        true_answer = {}
        data = json.loads(file.read())
        true_answer[str(id)] = ans
        data_ans = {**data, **true_answer}
        print(data_ans)

    with open('data/quizs.json', 'w') as zapis:
        json.dump(data_ans, zapis, indent=4)


def read_true_ans(id):
    with open('data/quizs.json') as file:
        dict = json.load(file)
        values = dp.values(dict, str(id))
        return values


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


@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    if pollAnswer.to_dict()['option_ids'] == read_true_ans(pollAnswer.to_dict()['user']['id']):
        write_score(pollAnswer.to_dict()['user']['id'], 1)
    else:
        write_score(pollAnswer.to_dict()['user']['id'], -1)


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


@bot.message_handler(commands='res_quiz')
def read_score(message):
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
        for i in range(1, number + 1):
            stroka += f'{i}. {dp.values(id_and_name, list(sorted_dict.keys())[i - 1])[0]}'\
                      f' - {dp.values(sorted_dict, str(list(sorted_dict.keys())[i - 1]))[0]} \U0001F60E \n'

        bot.send_message(message.chat.id, f"\u203C\uFE0F your score - "
                                          f" {dp.values(sorted_dict, str(message.chat.id))[0]} \u203C\uFE0F \n \n{stroka}")


bot.polling(none_stop=True, interval=0)
