import telebot
from telebot import types
import sqltable
from datetime import datetime
bot = telebot.TeleBot('5563607419:AAFfH-vzlFs7fJqo2xlhVtCQLq4W_HyUrLY')


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

            elif call.data == 'operfunc':
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Посмотреть список открытых запросов", callback_data='requestlist')
                item2 = types.InlineKeyboardButton("Назад", callback_data='back')
                markup.add(item1, item2)
                bot.send_message(call.message.chat.id, text='Меню', reply_markup=markup)

            elif call.data == 'pick':
                bot.send_message(call.message.chat.id, "Введите номер запроса")
                bot.register_next_step_handler(call.message, askreqid)

            elif call.data == 'requestlist':
                reqread(call.message)

            elif call.data == 'userfunc':
                markup = types.InlineKeyboardMarkup()
                item1 = types.InlineKeyboardButton("Сделать запрос", callback_data='request')
                item2 = types.InlineKeyboardButton("Назад", callback_data='back')
                markup.add(item1, item2)
                bot.send_message(call.message.chat.id, text='Меню', reply_markup=markup)

            elif call.data == 'back':
                operchoice(call.message)

            elif call.data == 'request':
                bot.send_message(call.message.chat.id, "Напишите свой запрос:")
                bot.register_next_step_handler(call.message, requeststart)

            elif call.data == 'accept':
                reqid = call.message.text.split()[0]
                datareq = sqltable.getatt(reqid, 'request', 'reqid')
                if datareq[4] == 'open':
                    data = sqltable.getatt(call.message.chat.id, 'opers', 'userid')
                    sqltable.insertoper(reqid, call.message.chat.id)
                    bot.send_message(datareq[1], "Ваш запрос обрабатывается оператором: " + data[1])
                else:
                    bot.send_message(call.message.chat.id, 'Запрос уже не валиден')

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выполняется....",
                                  reply_markup=None)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="Выполняется....")
    except Exception as e:
        print(repr(e))


def askreqid(message):
    data = sqltable.getatt(message.text, 'request', 'reqid')
    if data:
        if data[4] == 'open':
            oper = sqltable.getatt(message.chat.id, 'opers', 'userid')
            sqltable.insertoper(message.text, message.chat.id)
            bot.send_message(data[1], 'Ваш запрос: №' + data[0] + '\n Обрабатывается оператором: ' + oper[1])
            bot.send_message(message.chat.id, 'Вы успешно назначились для запроса №' + data[0])
            operchoice(message)
        elif data[4] == 'proceed':
            oper = sqltable.getatt(data[3], 'opers', 'userid')
            bot.send_message(message.chat.id, 'Данный запрос уже обрабатывается другим оператором: ' + oper[1])
            operchoice(message)
        else:
            bot.send_message(message.chat.id, 'Данный запрос уже закрыт')
            operchoice(message)


def reqread(message):
    if sqltable.readreqlist():
        for i in sqltable.readreqlist():
            user = sqltable.getatt(i[1], 'users', 'userid')
            if not user:
                user = sqltable.getatt(i[1], 'opers', 'userid')
            bot.send_message(message.chat.id, 'Запрос №' + i[0] + '\n' +
                             'Пользователь: ' + user[1] + '\n' + i[3] +
                             '\n' + 'Почта: ' + user[2] + '\n' + 'Телефон: ' + user[3])

        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Взять запрос на себя", callback_data='pick')
        item2 = types.InlineKeyboardButton("Назад", callback_data='back')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, text='Меню', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Список открытых запросов пуст! Отличная работа')


def asklogin(message):
    try:
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
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка вызова, попробуйте выполнить команду еще раз \n "
                                              "Или обратитесь к администратору")
        bot.send_message(message.chat.id, "Введите логин")
        bot.register_next_step_handler(message, asklogin)
        print(repr(e))


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
    try:
        if message.contact:
            if not sqltable.getatt(message.chat.id, 'users', 'userid'):
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
                bot.send_message(message.chat.id, "Вы уже зарегистрированы")
                usermenu(message)
        else:
            bot.send_message(message.chat.id, "Ошибка, воспользуйтесь меню для распознования номера")
            sqltable.clearbdlist()
            asknumber(message, numberverify)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка вызова, попробуйте выполнить команду еще раз \n "
                                          "Или обратитесь к администратору")

        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        print(str(repr(e)) + ' ' + str(datetime_str))
        asknumber(message, numberverify)


def usermenu(message):
    if sqltable.getatt(message.chat.id, 'users', 'userid'):
        markup3 = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Отправить запрос", callback_data='request')
        markup3.add(item1)
        bot.send_message(message.chat.id, text='Что сделать?', reply_markup=markup3)
    elif sqltable.getatt(message.chat.id, 'opers', 'userid'):
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Сделать запрос", callback_data='request')
        item2 = types.InlineKeyboardButton("Назад", callback_data='back')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, text='Меню', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка регистрации, зарегестрируйтесь повторно:')
        variantreg(message)


def requeststart(message):
    try:
        data = sqltable.getlist('request')
        if data:
            lastindex = int(data[-1][0]) + 1
        else:
            lastindex = 1
        lastindex = sqltable.rightindex(lastindex)
        sqltable.insertreq(lastindex, message.chat.id, message.text)
        opers = sqltable.getlist('opers')
        user = sqltable.getatt(message.chat.id, 'users', 'userid')
        if not user:
            user = sqltable.getatt(message.chat.id, 'opers', 'userid')
        for i in opers:
            bot.send_message(i[0], 'Поступил новый запрос')
            bot.send_message(i[0], 'Пользователь: ' + user[1] + '\n' + message.text +
                             '\n' + 'Почта: ' + user[2] + '\n' + 'Телефон: ' + user[3])
            yesno(i[0], lastindex)
        bot.send_message(message.chat.id, 'Ваш запрос успешно создан \n Его номер №' + lastindex)
        usermenu(message)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка вызова, попробуйте выполнить команду еще раз \n "
                                          "Или обратитесь к администратору")

        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        print(str(repr(e)) + ' ' + str(datetime_str))
        usermenu(message)


def yesno(message, index):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Принять", callback_data='accept')
    item2 = types.InlineKeyboardButton("Отклонить", callback_data='cancel')
    markup.add(item1, item2)
    bot.send_message(message, text=index + ' :номер запроса. \n' + 'Примете запрос?', reply_markup=markup)


def operchoice(message):
    if sqltable.getatt(message.chat.id, 'opers', 'userid'):
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Пользователя", callback_data='userfunc')
        item2 = types.InlineKeyboardButton("Оператора", callback_data='operfunc')
        item3 = types.InlineKeyboardButton("Админа", callback_data='admin')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, text='Какой функционал вы хотите?', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка регистрации, зарегестрируйтесь повторно:')
        variantreg(message)


bot.polling(non_stop=True, interval=0)
