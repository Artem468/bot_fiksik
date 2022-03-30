import telebot
import wikipedia
import math as m
from translate import Translator
from config import TOKEN


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(commands=["help"])
def helping(message):
    bot.send_message(message.chat.id, "бот может: \n искать в википедии "
                                      "\n выполнять математические действия"
                                      "\n переводить тексты")


@bot.message_handler(commands=["search"], content_types=["text"])
def search_in_wikipedia(message):
    try:
        request_in_wiki = message.text.split()
        wikipedia.set_lang(request_in_wiki[1])
        bot.send_message(message.chat.id, wikipedia.summary(request_in_wiki[2]))
    except Exception:
        try:
            bot.send_message(message.chat.id,
                             f"убедитесь в корректности запроса и запрашиваемого слова "
                             f"\nПример запроса: /search ru телеграмм \nВозможно вы имели в виду "
                             f"{wikipedia.suggest(request_in_wiki[2])}")
        except Exception:
            bot.send_message(message.chat.id, f"\nПример запроса: /search ru телеграм")


@bot.message_handler(commands=["calc"], content_types=["text"])
def calculator(message):
    try:
        bot.send_message(message.chat.id, eval(str(message.text[5:])))
    except Exception:
        bot.send_message(message.chat.id, "Проверьте правильность написания примера "
                                          "\nдоступные математические функции можно"
                                          " узнать по ссылке: https://pythonworld.ru/moduli/modul-math.html")


@bot.message_handler(commands=["translate"], content_types=["text"])
def tranlators(message):
    try:
        requests_in_translate = message.text.split()
        translator = Translator(from_lang=requests_in_translate[1], to_lang=requests_in_translate[2])
        translation = translator.translate((' '.join(requests_in_translate[3:])).lower())
        bot.send_message(message.chat.id, translation)
    except Exception:
        bot.send_message(message.chat.id, "Пример ввода: /translate en ru telegram"
                                          "\nиспользуются стандартные сокращения языков на "
                                          "английском языке, например:\n"
                                          "en - английский\n"
                                          "ru - русский\n"
                                          "и так далее")


bot.polling(none_stop=True, interval=0)
