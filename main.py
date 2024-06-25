import telebot
from telebot import types
import requests
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

link = 'https://www.cbr-xml-daily.ru/daily_json.js'

reply = requests.get(link)
Date = '-'.join(reply.json()['Date'][:10].split('-')[::-1])
USD = round(reply.json()['Valute']['USD']['Value'], 2)
EUR = round(reply.json()['Valute']['EUR']['Value'], 2)
GBP = round(reply.json()['Valute']['GBP']['Value'], 2)
TRY = round(reply.json()['Valute']['TRY']['Value'] / 10, 2)

d = {}
q = {}
def calculate_sell(amount, valute):
    res = 0
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
    res = 0
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
                     f'Курс валют ЦБ РФ\nна <b>{Date}</b>:\nДоллар - <b>{USD}</b>\nЕвро - <b>{EUR}</b>\nБританский фунт '
                     f'- <b>{GBP}</b>\nТурецкая лира - <b>{TRY}</b>',parse_mode='HTML')
    bot.send_message(message.chat.id, 'введите вашу сумму')
    q[message.chat.id] = False
    bot.register_next_step_handler(message, convert)

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
    text=f'-введите <b>новую сумму</b> чтобы посчитать снова\n-введите <b>start</b> чтобы вернуться к курсу валют'
    if call.data == 'USD/RUB' or call.data == 'EUR/RUB' or call.data == 'GBP/RUB' or call.data == 'TRY/RUB':
        res = calculate_sell(amount, value[0])
        bot.send_message(call.message.chat.id,
                         f'Готово-<b>{res}</b> ₽ \n',parse_mode='HTML')

    else:
        res = calculate_buy(amount, value[1])
        bot.send_message(call.message.chat.id,
                         f'Готово-{res} {value[1]} \n')

    if q[chat_id] == False:
        q[chat_id] = True
        bot.send_message(call.message.chat.id,f'{text}',parse_mode='HTML')
        bot.register_next_step_handler(call.message, question)

def question(message):
    reply=message.text
    if reply=='start':
        start(message)
    else:
        convert(message)

if __name__ == '__main__':
    print('Бот запущен')
    bot.polling(none_stop=True)
