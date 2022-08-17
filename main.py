"""
Модуль, в котором реализованы методы телеграмм бота MyReqBot
"""
import telebot
from telebot import types
import sqltable
from datetime import datetime
bot = telebot.TeleBot('5563607419:AAFfH-vzlFs7fJqo2xlhVtCQLq4W_HyUrLY')


@bot.message_handler(commands=['start'])
def start(message):
    """
    start(message) - функция для начала работы с телеграмм ботом
    :param message: Данные последнего отосланного пользователем сообщения
    """
    markup3 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Начать", callback_data='begin')
    markup3.add(item1)
    bot.send_message(message.chat.id, text='Начинаем?', reply_markup=markup3)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    callback_inline(call) - функция-агрегатор для распознования нажатий на инлайн-кнопки
    :param call: Данные нажатия инлайн кнопки
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
    try:
        if call.message:
            values = call.data.split()
            match values[0]:
                case "begin":
                    verify(call.message)
                case "user":
                    asknumber(call.message, numberverify)
                case "oper":
                    bot.send_message(call.message.chat.id, "Введите логин")
                    bot.register_next_step_handler(call.message, asklogin)
                case "operfunc":
                    operfunc(call.message)
                case "pick":
                    askreqid(call.message)
                case "requestlist":
                    reqread(call.message)
                case "userfunc":
                    usermenu(call.message)
                case "back":
                    operchoice(call.message)
                case "request":
                    bot.send_message(call.message.chat.id, "Напишите свой запрос:")
                    bot.register_next_step_handler(call.message, requeststart)
                case "accept":
                    accept(call.message)
                case "myrequest":
                    myreqread(call.message)
                case "№":
                    myreqfunc(call)
                case "chat":
                    chatstart(call)
                case "reopen":
                    reopen(call)
                case "close":
                    close(call)
                case _:
                    chsopenreq(call)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='f',
                                  reply_markup=None)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="Выполняется....")
    except Exception as e:
        bot.send_message(call.message.chat.id, "Ошибка вызова, попробуйте выполнить "
                                               "команду еще раз \n Или обратитесь к администратору")
        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'callback_inline')


def verify(message):
    """
    verify(message) - фунция для проверки пользователя на его существование в бд
    :param message: Данные последнего отосланного пользователем сообщения
    """
    if sqltable.getatt(message.chat.id, 'users', 'userid'):
        usermenu(message)
    elif sqltable.getatt(message.chat.id, 'opers', 'userid'):
        operchoice(message)
    else:
        variantreg(message)


def variantreg(message):
    """
    variantreg(message) - функция-интерфейс выбора типа регистрации
    :param message: Данные последнего отосланного пользователем сообщения
    """
    markup3 = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Я пользователь", callback_data='user')
    item2 = types.InlineKeyboardButton("Я оператор", callback_data='oper')
    markup3.add(item1, item2)
    bot.send_message(message.chat.id, text='Как вы хотите зарегистрироваться?', reply_markup=markup3)


def asknumber(message, func):
    """
    asknumber(message, func) - функция-интерфейс для получения номера телефона от пользователя
    :param message: Данные последнего отосланного пользователем сообщения
    :param func: Функция в которую переходит номер телефона для дальнейшей регистрации
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)
    try:
        nomer = bot.send_message(message.chat.id,
                                 'Чтобы зарегестрироваться отправьте свой номер телефона',
                                 reply_markup=keyboard)
        bot.register_next_step_handler(nomer, func)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка, воспользуйтесь меню для распознования номера")
        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'asknumber')
        asknumber(message, func)


@bot.message_handler(content_types=["contact"])
def numberverify(message):
    """
    numberverify(message) - функция для проверки пользователя на его существование в бд при сбрасывания им номера
    :param message: Данные последнего отосланного пользователем сообщения
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
    try:
        if message.contact:
            if sqltable.getatt(message.chat.id, 'users', 'userid') or \
                    sqltable.getatt(message.chat.id, 'opers', 'userid'):
                bot.send_message(message.chat.id, "Вы уже зарегистрированы")
                usermenu(message)
            else:
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
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка вызова, попробуйте выполнить команду еще раз \n "
                                          "Или обратитесь к администратору")

        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'numberverify')
        asknumber(message, numberverify)


def usermenu(message):
    """
    usermenu(message) - функция-интерфейс для создания запроса
    :param message: Данные последнего отосланного пользователем сообщения
    """
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
    """
    requeststart(message) - функция для занесения в бд запроса и последующей его отправки операторам
    :param message: Данные последнего отосланного пользователем сообщения
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
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
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'requeststart')
        usermenu(message)


def yesno(message, index):
    """
    yesno(message) - функция-интерфейс для принятие/отклонения поступающего запроса
    :param message: Данные последнего отосланного пользователем сообщения
    :param index: Номер запроса, который приходит оператору и записывается в бд
    """
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Принять", callback_data='accept')
    item2 = types.InlineKeyboardButton("Отклонить", callback_data='cancel')
    markup.add(item1, item2)
    bot.send_message(message, text=index + ' :номер запроса. \n' + 'Примете запрос?', reply_markup=markup)


def accept(message):
    """
    accept(message) - функция закрепляющая оператора за актуальным запросом
    :param message: Данные последнего отосланного пользователем сообщения
    """
    reqid = message.text.split()[0]
    datareq = sqltable.getatt(reqid, 'request', 'reqid')
    if datareq[4] == 'open':
        data = sqltable.getatt(message.chat.id, 'opers', 'userid')
        sqltable.insertoper(reqid, message.chat.id)
        bot.send_message(datareq[1], "Ваш запрос обрабатывается оператором: " + data[1])
        operchoice(message)
    else:
        bot.send_message(message.chat.id, 'Запрос уже не валиден')
        operchoice(message)


def asklogin(message):
    """
    asklogin(message) - функция для регистрации пользователя через логин
    :param message: Данные последнего отосланного пользователем сообщения
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
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

        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'asklogin')
        bot.send_message(message.chat.id, "Введите логин")
        bot.register_next_step_handler(message, asklogin)


def operchoice(message):
    """
    operchoice(message) - функция-интерфейс для выбора оператором роли
    :param message: Данные последнего отосланного пользователем сообщения
    """
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


def operfunc(message):
    """
    operfunc(message) - функция-интерфейс взаимодействия со списками запросов
    :param message: Данные последнего отосланного пользователем сообщения
    """
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Посмотреть список открытых запросов", callback_data='requestlist')
    item2 = types.InlineKeyboardButton("Посмотреть список моих запросов", callback_data='myrequest')
    item3 = types.InlineKeyboardButton("Назад", callback_data='back')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, text='Меню', reply_markup=markup)


def reqread(message):
    """
    reqread(message) - функция-интерфейс для вывода списка открытых запросов
    :param message: Данные последнего отосланного пользователем сообщения
    """
    if sqltable.readreqlist():
        for i in sqltable.readreqlist():
            userreqsendmsg(i, message)
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Взять запрос на себя", callback_data='pick')
        item2 = types.InlineKeyboardButton("Назад", callback_data='back')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, text='Меню', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Список открытых запросов пуст! Отличная работа')


def userreqsendmsg(userid, message):
    """
    userreqsendmsg(message) - функция для отправки оператору списка запросов
    :param userid: Кортеж содержащий id телеграмм пользователя отправившего запрос
    :param message: Данные последнего отосланного пользователем сообщения
    """
    user = sqltable.getatt(userid[1], 'users', 'userid')
    if not user:
        user = sqltable.getatt(userid[1], 'opers', 'userid')
    bot.send_message(message.chat.id, 'Запрос №' + userid[0] + '\n' +
                     'Пользователь: ' + user[1] + '\n' + userid[3] +
                     '\n' + 'Почта: ' + user[2] + '\n' + 'Телефон: ' + user[3])


def askreqid(message):
    """
    askreqid(message) - функция-интерфейс для выбора нужного из открытых запросов
    :param message: Данные последнего отосланного пользователем сообщения
    """
    data = sqltable.readreqlist()
    if data:
        markup = types.InlineKeyboardMarkup()
        if type(data) == list:
            for i in data:
                item = types.InlineKeyboardButton(str(i[0]), callback_data=str(i[0]))
                markup.add(item)
        else:
            item = types.InlineKeyboardButton(str(data[0]), callback_data=str(data[0]))
            markup.add(item)
        item1 = types.InlineKeyboardButton('Назад', callback_data='back')
        markup.add(item1)
        bot.send_message(message.chat.id, text='Выберите запрос', reply_markup=markup)


def chsopenreq(call):
    """
    chsopenreq(call) - функция регистрации оператора за запросом в бд
    :param call: Данные нажатия инлайн кнопки
    """
    if sqltable.getatt(call.data, 'request', 'reqid')[4] == 'open':
        request = sqltable.getatt(call.data, 'request', 'reqid')
        oper = sqltable.getatt(call.message.chat.id, 'opers', 'userid')
        sqltable.insertoper(call.data, call.message.chat.id)
        bot.send_message(request[1], 'Ваш запрос обрабатывается оператором: ' + oper[1])
        bot.send_message(call.message.chat.id, 'Вы обрабатываете запрос №' + call.data)
        operchoice(call.message)
    else:
        bot.send_message(call.message.chat.id, 'Запрос уже не валиден')
        operchoice(call.message)


def myreqread(message):
    """
    myreqread(message) - функция-интерфейс для выбора нужного из взятых запросов
    :param message: Данные последнего отосланного пользователем сообщения
    """
    if sqltable.readmyreqlist(str(message.chat.id)):
        idcollection = []
        for i in sqltable.readmyreqlist(str(message.chat.id)):
            userreqsendmsg(i, message)
            idcollection.append(i[0])
        markup = types.InlineKeyboardMarkup()
        for j in idcollection:
            item = types.InlineKeyboardButton(str(j), callback_data='№ '+str(j))
            markup.add(item)
        item = types.InlineKeyboardButton("Назад", callback_data='back')
        markup.add(item)
        bot.send_message(message.chat.id, text='Выберите запрос из списка', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Список ваших запросов пуст, '
                                          'проверьте наличие запросов в ближайшее время')


def myreqfunc(call):
    """
    myreqfunc(call) - функция-интерфейс для выбора опций над выбранным запросом
    :param call: Данные нажатия инлайн кнопки
    """
    number = call.data.split()[1]
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Закрыть запрос", callback_data='close ' + number)
    item2 = types.InlineKeyboardButton("Снять с себя запрос", callback_data='reopen ' + number)
    item3 = types.InlineKeyboardButton("Открыть чат с пользователем", callback_data='chat ' + number)
    item4 = types.InlineKeyboardButton("Назад", callback_data='back')
    markup.add(item1, item2, item3, item4)
    bot.send_message(call.message.chat.id, text='Запрос №' + number, reply_markup=markup)


def close(call):
    """
    close(call) - функция закрывающая запрос
    :param call: Данные нажатия инлайн кнопки
    """
    reqid = call.data.split()[1]
    user = sqltable.getatt(reqid, 'request', 'reqid')[1]
    sqltable.closereq(reqid)
    bot.send_message(user, 'Ваш запрос №' + reqid + ' закрыт')
    bot.send_message(call.message.chat.id, 'Запрос успешно закрыт')
    operchoice(call.message)


def reopen(call):
    """
    reopen(call) - функция заново открывающая запрос
    :param call: Данные нажатия инлайн кнопки
    """
    reqid = call.data.split()[1]
    user = sqltable.getatt(reqid, 'request', 'reqid')[1]
    sqltable.resreq(reqid)
    bot.send_message(user, 'Оператор снял ваш запрос №' + reqid
                     + ', мы вам сообщим когда его возьмет новый оператор')
    bot.send_message(call.message.chat.id, 'Запрос успешно открыт')
    operchoice(call.message)


def chatstart(call):
    """
    chatstart(call) - функция соединяющая оператора и пользователя с помощью чата
    :param call: Данные нажатия инлайн кнопки
    """
    user = sqltable.getatt(call.data.split()[1], 'request', 'reqid')[1]
    sqltable.createconnection(user, str(call.message.chat.id))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("БОТ СТОП")
    markup.add(btn1)
    bot.send_message(call.message.chat.id, 'Чтобы закрыть чат напишите БОТ СТОП', reply_markup=markup)
    bot.send_message(call.message.chat.id, 'Чат с пользователем открыт')
    bot.send_message(user, 'По вашему запросу открыт чат с оператором:')
    bot.register_next_step_handler(call.message, chat)


def chat(message):
    """
    chat(message) - функция пересылающая сообщения оператора пользователю при присутствии соединения
    :param message: Данные последнего отосланного пользователем сообщения
    :exception e: Данные об произошедшей ошибке, сразу записываются в таблицу log базы данных с временным отпечатком
    """
    try:
        if message.text == 'БОТ СТОП':
            user = sqltable.getatt(str(message.chat.id), 'connections', 'operid')[0]
            sqltable.deleteconnection(str(message.chat.id))
            bot.send_message(message.chat.id, 'Соединение успешно закрыто')
            bot.send_message(user, 'Оператор закрыл с вами чат')
            operchoice(message)
        else:
            user = sqltable.getatt(str(message.chat.id), 'connections', 'operid')[0]
            bot.send_message(user, message.text)
            bot.register_next_step_handler(message, chat)
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка вашего сообщения \n Убедитесь что отправляете текст!")
        bot.send_message(message.chat.id, "Или обратитесь к администратору")
        datetime_str = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        sqltable.loginsert(str(repr(e)), str(datetime_str), 'chat')


@bot.message_handler(content_types=['text'])
def userchat(message):
    """
    userchat(message) - функция пересылающая сообщения пользователя оператору при присутствии соединения
    :param message: Данные последнего отосланного пользователем сообщения
    """
    if sqltable.getatt(str(message.chat.id), 'connections', 'userid'):
        oper = sqltable.getatt(str(message.chat.id), 'connections', 'userid')[1]
        bot.send_message(int(oper), message.text)


bot.polling(non_stop=True, interval=0)
