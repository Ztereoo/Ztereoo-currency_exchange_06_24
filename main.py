import telebot
from telebot import types
import requests
import os
import sys
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

link = 'https://www.cbr-xml-daily.ru/daily_json.js'

reply = requests.get(link)
Date = reply.json()['Date']
USD = round(reply.json()['Valute']['USD']['Value'], 2)
EUR = round(reply.json()['Valute']['EUR']['Value'], 2)
GBP = round(reply.json()['Valute']['GBP']['Value'], 2)
TRY = round(reply.json()['Valute']['TRY']['Value'] / 10, 2)

d = {}
q = {}


def calculate_sell(amount, valute):
    res = ''
    if valute == 'USD':
        res = amount * USD
    elif valute == 'EUR':
        res = amount * EUR
    elif valute == 'GBP':
        res = amount * GBP
    elif valute == 'TRY':
        res = amount * TRY
    return round(res, 2)


def calculate_buy(amount, valute):
    res = ''
    if valute == 'USD':
        res = amount / USD
    elif valute == 'EUR':
        res = amount / EUR
    elif valute == 'GBP':
        res = amount / GBP
    elif valute == 'TRY':
        res = amount / TRY
    return round(res, 2)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f'Курс валют ЦБ РФ\nна {Date[:10]}:\nДоллар - {USD}\nЕвро - {EUR}\nБританский фунт - {GBP}\nТурецкая лира - {TRY}')
    bot.send_message(message.chat.id, 'введите число, чтобы рассчитать сумму')
    q[message.chat.id] = False
    bot.register_next_step_handler(message, convert)


@bot.message_handler(commands=['restart'])
def restart_bot(message):
    bot.reply_to(message, "Бот перезапустился...")
    bot.send_message(message.chat.id, f'Введите /start чтобы начать еще раз')
    os.execv(sys.executable, ['python'] + sys.argv)


def convert(message):
    try:
        amount = int(message.text.strip())
        chat_id = message.chat.id
        d[chat_id] = amount
        q[chat_id] = False

    except ValueError:
        bot.send_message(message.chat.id, 'введите положительное число')
        bot.register_next_step_handler(message, convert)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/RUB', callback_data='USD/RUB')
        btn2 = types.InlineKeyboardButton('EUR/RUB', callback_data='EUR/RUB')
        btn3 = types.InlineKeyboardButton('GBP/RUB', callback_data='GBP/RUB')
        btn4 = types.InlineKeyboardButton('TRY/RUB', callback_data='TRY/RUB')
        markup.add(btn1, btn2, btn3, btn4)
        btn5 = types.InlineKeyboardButton('RUB/USD', callback_data='RUB/USD')
        btn6 = types.InlineKeyboardButton('RUB/EUR', callback_data='RUB/EUR')
        btn7 = types.InlineKeyboardButton('RUB/GBP', callback_data='RUB/GBP')
        btn8 = types.InlineKeyboardButton('RUB/TRY', callback_data='RUB/TRY')
        markup.add(btn5, btn6, btn7, btn8)
        bot.send_message(message.chat.id, "Выберите пару валют",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Число должно быть положительное')
        bot.register_next_step_handler(message, convert)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    value = call.data.split('/')
    chat_id = call.message.chat.id
    amount = d[chat_id]
    if call.data == 'USD/RUB' or call.data == 'EUR/RUB' or call.data == 'GBP/RUB' or call.data == 'TRY/RUB':
        res = calculate_sell(amount, value[0])
        bot.send_message(call.message.chat.id,
                         f'Готово-{res} ₽\nМожем посчитать еще ')

    else:
        res = calculate_buy(amount, value[1])
        bot.send_message(call.message.chat.id,
                         f'Готово-{res} {value[1]}\nМожем посчитать еще ')

    if q[chat_id] == False:
        q[chat_id] = True
        bot.register_next_step_handler(call.message, convert)


if __name__ == '__main__':
    print('Бот запущен')
    bot.polling(none_stop=True)
