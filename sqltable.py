import sqlite3


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
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS bdlist(
    fio TEXT, 
    mail TEXT,
    numbers TEXT);""")
    conn.commit()
    conn.close()


def updatingbd():
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
            insert(name, email, number, 'bdlist')
        line = text.readline()
    text.close()


def getatt(att, table, tableatt):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM """ + table + """ WHERE """ + tableatt + """='""" + sqlprevent(str(att)) + """';""")
    one_result = cur.fetchone()
    conn.close()
    return one_result


def getlist(table):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM """ + table + """;""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def insertreq(reqid, userid, reqtext):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO request VALUES(
    '""" + reqid + """', '""" + str(userid) + """', '-', '""" + sqlprevent(reqtext) + """', 'open');""")
    conn.commit()
    conn.close()


def insert(fio, email, number, table):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO """ + table + """ VALUES(
    '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()
    conn.close()


def insertuser(userid, fio, email, number, table):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO """ + table + """ VALUES(
        '""" + str(userid) + """', '""" + fio + """', '""" + email + """', '""" + str(number) + """');""")
    conn.commit()
    conn.close()


def clearbdlist():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
    conn.close()


def insertoper(reqid, operid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET operid='""" + str(operid) + """' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    cur.execute("""UPDATE request SET status='proceed' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def readreqlist():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE status='open';""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def readmyreqlist(userid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE status='proceed' AND operid='""" + userid + """';""")
    all_result = cur.fetchall()
    conn.close()
    return all_result


def closereq(reqid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET status='closed' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def resreq(reqid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""UPDATE request SET status='open' WHERE reqid='""" + reqid + """';""")
    conn.commit()
    conn.close()


def rightindex(index):
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
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO log VALUES('""" + sqlprevent(error) + """', '""" + date + """', '""" + func + """');""")
    conn.commit()
    conn.close()


def sqlprevent(sentence):
    newsen = ''
    for i in sentence:
        if i not in """'""" and i not in '"':
            newsen += i
    return newsen


def createconnection(userid, operid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO connections VALUES('""" + userid + """', '""" + operid + """');""")
    conn.commit()
    conn.close()


def deleteconnection(operid):
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DELETE FROM connections WHERE operid='""" + operid + """';""")
    conn.commit()
    conn.close()
