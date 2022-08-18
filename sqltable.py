"""
Модуль для взаимодействия с базой данных SQLLite
"""
import sqlite3


def numbermaker(numbers):
    """
    numbermaker(numbers) - функция преобразования номера телефона в удобный для телеграма формат
    :param numbers: Тип str, номер телефона в любом формате
    :return: Тип str, номер телефона начинающийся с 7
    """
    number = ''
    for j in range(len(numbers)):
        if numbers[j] not in '()+':
            if numbers[j] == '8' and str(j) == '0':
                number += '7'
            else:
                number += numbers[j]
    return number


def createbdlist():
    """
    createbdlist() - функция создания теневой таблицы с колонками для заполнения данных из 1с
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS bdlist(
    fio TEXT, 
    mail TEXT,
    numbers TEXT);""")
    conn.commit()
    conn.close()


def updatingbd():
    """
    updatingbd() - функция заполнения теневой таблицы bdlist данными о сотрудниках из 1с
    """
    createbdlist()
    crntfile = r'Список.txt'
    text = open(crntfile, 'r', encoding="utf8")
    line = text.readline()
    while line != '':
        if len(line.split()) > 4:
            if len(line.split()) == 5:
                number = numbermaker(line.split()[4])
                name = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2]
                email = line.split()[3]
            else:
                numberlist = ''
                for i in line.split()[4:]:
                    numberlist += i
                number = numbermaker(numberlist)
                name = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2]
                email = line.split()[3]
            insert(name, email, number)
        line = text.readline()
    text.close()


def clearbdlist():
    """
    clearbdlist() - функция удаляющая теневую таблицу bdlist базы данных
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
    conn.close()


def getatt(att, table, tableatt):
    """
    getatt(att, table, tableatt) - функция получения строки таблицы содержащий нужный атрибут в нужной колонке
    :param att: Тип конвертируемый в str, атрибут, который возможно есть в таблице базы данных
    :param table: Тип str, название таблицы базы данных
    :param tableatt: Тип str, название столбца таблицы базы данных
    :return: Тип кортеж, строка с нужным атрибутом в нужной строке, если искомого атрибута в столбце нет, возвращает None
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM """ + table + """ WHERE """ + tableatt + """='""" + sqlprevent(str(att)) + """';""")
    one_result = cur.fetchone()
    conn.close()
    return one_result


def getlist(table):
    """
    getlist(table) - функция получения всех значений таблицы базы данных
    :param table: Тип str, искомая таблица базы данных
    :return: Тип массив из кортежей, возвращает массив из строк таблицы базы данных(кортежи)
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM """ + table + """;""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def insertreq(reqid, userid, reqtext):
    """
    insertreq(reqid, userid, reqtext) - функция вставляющая в таблицу request базы данных запрос
    :param reqid: Тип str, номер запроса
    :param userid: Тип int, телеграмм id пользователя
    :param reqtext: Тип str, текст запроса
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO request VALUES(
    '""" + reqid + """', '""" + str(userid) + """', '-', '""" + sqlprevent(reqtext) + """', 'open');""")
    conn.commit()
    conn.close()


def insert(fio, email, number):
    """
    insert(fio, email, number) - функция вставляющая пользователя в таблицу bdlist базы данных сотрудника из 1с
    :param fio: Тип str, ФИО сотрудника
    :param email: Тип str, почта сотрудника
    :param number: Тип str/int, номер телефона сотрудника
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO bdlist VALUES(
    '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()
    conn.close()


def insertuser(userid, fio, email, number, table):
    """
    insertuser(userid, fio, email, number, table) - функция вставляющая в нужную таблицу базы данных пользователя системы
    :param userid: Тип int, телеграмм id пользователя
    :param fio: Тип str, ФИО пользователя
    :param email: Тип str, почта пользователя
    :param number: Тип str/int, номер телефона пользователя
    :param table: Тип str, название таблицы
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO """ + table + """ VALUES(
        '""" + str(userid) + """', '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()
    conn.close()


def insertoper(reqid, operid):
    """
    insertoper(reqid, operid) - функция закрепляющая в таблице request базы данных оператора за запросом
    :param reqid: Тип str, номер запроса
    :param operid: Тип int, телеграмм id оператора
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET operid='""" + str(operid) + """' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    cur.execute("""UPDATE request SET status='proceed' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def readreqlist():
    """
    readreqlist() - функция возвращающая все открытые запросы
    :return: Тип массив из кортежей, содержащий все открытые запросы в виде кортежа
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE status='open';""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def readmyreqlist(operid):
    """
    readmyreqlist(userid) - функция возвращающая все запросы висящие на операторе
    :param operid: Тип int, телеграмм id оператора
    :return: Тип массив из кортежей, содержащий запросы в виде кортежа
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE status='proceed' AND operid='""" + str(operid) + """';""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def closereq(reqid):
    """
    closereq(reqid) - функция обновляющая статус запроса, меняя его на closed
    :param reqid: Тип str, номер запроса
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET status='closed' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def resreq(reqid):
    """
    resreq(reqid) - функция обновляющая статус запроса, меняя его на open
    :param reqid: Тип str, номер запроса
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET status='open' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def rightindex(index):
    """
    rightindex(index) - функция правильно создающая 5-значный номер запроса
    :param index: Тип int, обычный номер запроса
    :return: Тип str, 5-значный номер запроса
    """
    if 1 <= index/10 and index/100 < 1:
        index = '000' + str(index)
    elif 1 <= index/100 and index/1000 < 1:
        index = '00' + str(index)
    elif 1 <= index/1000 and index/10000 < 1:
        index = '0' + str(index)
    elif 1 <= index/10000:
        index = str(index)
    else:
        index = '0000' + str(index)
    return index


def loginsert(error, date, func):
    """
    loginsert(error, date, func) - функция вписывающая ошибки в таблицу log базы данных
    :param error: Тип str, текст ошибки
    :param date: Тип str, временной отпечаток точностью до секунды
    :param func: Тип str, название функции, в которой вышла ошибка
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO log VALUES('""" + sqlprevent(error) + """', '""" + date + """', '""" + func + """');""")
    conn.commit()
    conn.close()


def sqlprevent(sentence):
    """
    sqlprevent(sentence) - функция, предотвращающая sql-инъекции
    :param sentence: Тип str, строка входящая в базу данных
    :return: Тип str, новая строка, не содержащая ' "
    """
    newsen = ''
    for i in sentence:
        if i not in """'""" and i not in '"':
            newsen += i
    return newsen


def createconnection(userid, operid):
    """
    createconnection(userid, operid) - функция, вписывающая id пользователя и оператора в таблицу connections базы данных
    :param userid: Тип str, телеграмм id пользователя
    :param operid: Тип str, телеграмм id оператора
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO connections VALUES('""" + userid + """', '""" + operid + """');""")
    conn.commit()
    conn.close()


def deleteconnection(operid):
    """
    deleteconnection(operid) - функция, удаляющая соединение между пользователями
    :param operid: Тип str, телеграмм id оператора
    """
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DELETE FROM connections WHERE operid='""" + operid + """';""")
    conn.commit()
    conn.close()
