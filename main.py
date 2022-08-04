import telebot
bot = telebot.TeleBot('5563607419:AAFfH-vzlFs7fJqo2xlhVtCQLq4W_HyUrLY')
from telebot import types
import clist
import sqltable


@bot.message_handler(commands=['start'])
def start(message):
    markup3 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Начать", callback_data='begin')
    markup3.add(item1)
    bot.send_message(message.chat.id, text='Начинаем?', reply_markup=markup3)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):  # TODO персонализировать преобразование кнопок
    try:
        if call.message:
            if call.data == 'begin':
                bot.send_message(call.message.chat.id, 'Вот и отличненько ')
                verify(call.message)

            elif call.data == 'user':
                asknumber(call.message, numberverify)

            elif call.data == 'oper':
                bot.send_message(call.message.chat.id, "Введите логин")
                bot.register_next_step_handler(call.message, asklogin)

            elif call.data == 'request':
                bot.send_message(call.message.chat.id, "Напишите свой запрос:")
                bot.register_next_step_handler(call.message, requeststart)

            elif call.data == 'accept':
                userid = clist.closerequest()
                file = open(r'bdlistoper.txt', 'r', encoding="utf8")
                line = file.readline()
                while line != '':
                    if str(call.message.chat.id) == line.split()[-1:][0]:
                        opername = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2]
                        break
                    line = file.readline()
                bot.send_message(userid, "Ваш запрос обрабатывается оператором: " + opername)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выполняется....",
                                  reply_markup=None)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="Выполняется....")
    except Exception as e:
        print(repr(e))


def asklogin(message):
    if sqltable.getatt(message.text, 'operdb', 'login'):
        datas = sqltable.getatt(message.text, 'operdb', 'login')
        sqltable.updatingbd()
        if sqltable.getatt(datas[1], 'bdlist', 'numbers'):
            data = sqltable.getatt(datas[1], 'bdlist', 'numbers')
            sqltable.insertuser(message.chat.id, data[0], data[1], data[2], 'opers')
            bot.send_message(message.chat.id, "Вы успешно зарегестрированы, добро пожаловать в систему")
            sqltable.clearbdlist()
            operchoice(message)
        else:
            bot.send_message(message.chat.id, "Произошла ошибка, обратитесь к администратору")
            sqltable.clearbdlist()
    else:
        bot.send_message(message.chat.id, "Произошла ошибка, обратитесь к администратору")


def verify(message):
    if sqltable.getatt(message.chat.id, 'users', 'userid'):
        usermenu(message)
    elif sqltable.getatt(message.chat.id, 'opers', 'userid'):
        operchoice(message)
    else:
        variantreg(message)


def variantreg(message):
    markup3 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Я пользователь", callback_data='user')
    item2 = types.InlineKeyboardButton("Я оператор", callback_data='oper')
    markup3.add(item1, item2)
    bot.send_message(message.chat.id, text='Как вы хотите зарегистрироваться?', reply_markup=markup3)


def asknumber(message, func):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)
    try:
        nomer = bot.send_message(message.chat.id,
                                 'Чтобы зарегестрироваться отправьте свой номер телефона',
                                 reply_markup=keyboard)
        bot.register_next_step_handler(nomer, func)
    except:
        bot.send_message(message.chat.id, "Ошибка, воспользуйтесь меню для распознования номера")
        asknumber(message, func)


@bot.message_handler(content_types=["contact"])
def numberverify(message):
    if message.contact:
        sqltable.updatingbd()
        if sqltable.getatt(message.contact.phone_number, 'bdlist', 'numbers'):
            data = sqltable.getatt(message.contact.phone_number, 'bdlist', 'numbers')
            sqltable.insertuser(message.chat.id, data[0], data[1], data[2], 'users')
            bot.send_message(message.chat.id, "Вы успешно зарегестрированы, добро пожаловать в систему")
            sqltable.clearbdlist()
            usermenu(message)
        else:
            bot.send_message(message.chat.id, "Произошла ошибка, обратитесь к администратору")
            sqltable.clearbdlist()

    else:
        bot.send_message(message.chat.id, "Ошибка, воспользуйтесь меню для распознования номера")
        sqltable.clearbdlist()
        asknumber(message, numberverify)


def usermenu(message):
    if sqltable.getatt(message.chat.id, 'users', 'userid'):
        markup3 = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Отправить запрос", callback_data='request')
        markup3.add(item1)
        bot.send_message(message.chat.id, text='Что сделать?', reply_markup=markup3)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка регистрации, зарегестрируйтесь повторно:')
        asknumber(message, numberverify)


def requeststart(message):
    request = open(r'requests.txt', 'r', encoding="utf8")
    line = request.readline()
    count = 0
    while line != '':
        count += 1
        line = request.readline()
    request.close()
    count += 1
    request = open(r'requests.txt', 'a', encoding="utf8")
    request.write(message.text + ' ' + str(message.chat.id) + ' ' + str(count) + ' open \n')
    request.close()
    opers = open(r'bdlistoper.txt', 'r', encoding="utf8")
    line = opers.readline()
    while line != '':
        bot.send_message(line.split()[4], 'Поступил новый запрос')
        bot.send_message(line.split()[4], message.text)
        yesno(line.split()[4])
        line = opers.readline()
    opers.close()


def yesno(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Принять", callback_data='accept')
    item2 = types.InlineKeyboardButton("Отклонить", callback_data='cancel')
    markup.add(item1, item2)
    bot.send_message(message, text='Примете запрос?', reply_markup=markup)


def operchoice(message):  # TODO переделать кнопки и сделать проверку на апдейте базы перед запросом
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Пользователя")
    btn2 = types.KeyboardButton("Оператора")
    btn3 = types.KeyboardButton("Админа")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id,
                     text="Какой функционал вы хотите?"
                     .format(message.from_user), reply_markup=markup)
    bot.register_next_step_handler(message, yesno)

'''
def operfunc(message):  # TODO расписать функционал оператора
    if message.text == "Пользователя":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Отправить запрос")
        btn2 = types.KeyboardButton("Назад")
        markup.add(btn1, btn2) 
        bot.send_message(message.chat.id,
                         text="Что сделать?"
                         .format(message.from_user), reply_markup=markup)
        bot.register_next_step_handler(message, useroperrequest)
    elif message.text == "Оператора":
        pass
    elif message.text == "Админа":
        pass
    else:
        pass
'''
bot.polling(non_stop=True, interval=0)
