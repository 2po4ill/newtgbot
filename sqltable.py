import sqlite3  # TODO для модерирования в ирл сделать закрытие и открытие соединения в каждой функции

conn = sqlite3.connect('tgbot.db', check_same_thread=False)
cur = conn.cursor()


def numbermaker(numbers):
    number = ''
    for j in range(len(numbers)):
        if numbers[j] not in '()+':
            if numbers[j] == '8' and str(j) == '0':
                number += '7'
            else:
                number += numbers[j]
    return number


def createbdlist():
    cur.execute("""CREATE TABLE IF NOT EXISTS bdlist(
    fio TEXT, 
    mail TEXT,
    numbers TEXT);""")
    conn.commit()


def updatingbd():  # TODO пересмотреть надобность if на 28
    createbdlist()
    crntfile = r'Список.txt'
    text = open(crntfile, 'r', encoding="utf8")
    line = text.readline()
    while line != '':
        if len(line.split()) > 4:
            if line.split()[4][0] in '+789':
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
            insert(name, email, number, 'bdlist')
        line = text.readline()
    text.close()


def getatt(att, table, tableatt):
    cur.execute("""SELECT * FROM """ + table + """ WHERE """ + tableatt + """='""" + str(att) + """';""")
    one_result = cur.fetchone()
    return one_result


def insert(fio, email, number, table):
    cur.execute("""INSERT INTO """ + table + """ VALUES(
    '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()


def insertuser(userid, fio, email, number, table):
    cur.execute("""INSERT INTO """ + table + """ VALUES(
        '""" + str(userid) + """', '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()


def clearbdlist():
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
