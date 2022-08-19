import pytest
import sqltable
import sqlite3


def test_numbermaker():
    numbers = ['89600681532', '+7(913)436216', '91754325']
    answer = []
    for i in numbers:
        answer.append(sqltable.numbermaker(i))
    assert answer == ['79600681532', '7913436216', '91754325']


def test_createbdlist():
    sqltable.createbdlist()
    try:
        conn = sqlite3.connect('tgbot.db', check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE bdlist(
            fio TEXT, 
            mail TEXT,
            numbers TEXT);""")
        conn.commit()
        conn.close()
        error = None
    except Exception as e:
        error = str(e)
    assert error == 'table bdlist already exists'
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
    conn.close()


@pytest.fixture()
def preparelist():
    crntfile = r'Список.txt'
    text = open(crntfile, 'w', encoding="utf8")
    text.write('a b e mail 789 \n')


def test_updatingbd(preparelist):
    sqltable.updatingbd()
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM bdlist WHERE numbers='789';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('a b e', 'mail', '789')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
    conn.close()


def test_clearbdlist():
    sqltable.createbdlist()
    sqltable.clearbdlist()
    try:
        conn = sqlite3.connect('tgbot.db', check_same_thread=False)
        cur = conn.cursor()
        cur.execute("""CREATE TABLE bdlist(
                    fio TEXT, 
                    mail TEXT,
                    numbers TEXT);""")
        conn.commit()
        conn.close()
        error = None
    except Exception as e:
        error = str(e)
    assert error is None
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE bdlist;""")
    conn.commit()
    conn.close()


def test_getatt():
    sqltable.createbdlist()
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""INSERT INTO bdlist VALUES(
    'a b e', 'mail', '789');""")
    conn.commit()
    conn.close()
    assert sqltable.getatt('789', 'bdlist', 'numbers') == ('a b e', 'mail', '789')
    sqltable.clearbdlist()


@pytest.fixture()
def answer():
    return [('a b e', 'mail', '789') for i in range(3)]


def test_getlist(answer):
    sqltable.createbdlist()
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    for i in range(3):
        cur.execute("""INSERT INTO bdlist VALUES(
                'a b e', 'mail', '789');""")
        conn.commit()
    assert sqltable.getlist('bdlist') == answer
    sqltable.clearbdlist()


@pytest.fixture()
def requestprep():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS request;""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS request(
        reqid TEXT, 
        userid TEXT,
        operid TEXT,
        text TEXT,
        status TEXT);""")
    conn.commit()
    conn.close()


def test_insertreq(requestprep):
    sqltable.insertreq('00001', '5435345', 'rajesh kutrapali')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE reqid='00001';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('00001', '5435345', '-', 'rajesh kutrapali', 'open')


def test_insert():
    sqltable.createbdlist()
    sqltable.insert('giorno', 'giovanna', 'ore wa pirate')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM bdlist WHERE fio='giorno';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('giorno', 'giovanna', 'ore wa pirate')
    sqltable.clearbdlist()


@pytest.fixture()
def userlist():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS users;""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
            userid TEXT, 
            fio TEXT,
            mail TEXT,
            numbers TEXT);""")
    conn.commit()
    conn.close()


def test_insertuser(userlist):
    sqltable.insertuser('88178', 'egor', 'milo', 'bumber', 'users')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM users WHERE fio='egor';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('88178', 'egor', 'milo', 'bumber')


def test_insertoper(requestprep):
    sqltable.insertreq('00001', '5435345', 'rajesh kutrapali')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE operid='-';""")
    one_result = cur.fetchone()
    flag = False
    if one_result:
        flag = True
    sqltable.insertoper('00001', '87156')
    cur.execute("""SELECT * FROM request WHERE operid='87156';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('00001', '5435345', '87156', 'rajesh kutrapali', 'proceed') and flag


@pytest.fixture()
def fill(requestprep):
    sqltable.insertreq('00001', '5435345', 'rajesh kutrapali')
    sqltable.insertreq('00002', '5435345', 'rajesh kutrapalo')
    sqltable.insertreq('00003', '5435345', 'rajesh kutrapale')
    return [('00001', '5435345', '-', 'rajesh kutrapali', 'open'),
            ('00002', '5435345', '-', 'rajesh kutrapalo', 'open'),
            ('00003', '5435345', '-', 'rajesh kutrapale', 'open')]


def test_readreqlist(fill):
    assert sqltable.readreqlist() == fill


@pytest.fixture()
def fillopers(fill):
    sqltable.insertoper('00001', '003')
    sqltable.insertoper('00003', '003')
    sqltable.insertoper('00002', '002')
    return [('00001', '5435345', '003', 'rajesh kutrapali', 'proceed'),
            ('00003', '5435345', '003', 'rajesh kutrapale', 'proceed')]


def test_readmyreqlist(fillopers):
    assert sqltable.readmyreqlist('003') == fillopers \
           and sqltable.readmyreqlist('002') == [('00002', '5435345', '002', 'rajesh kutrapalo', 'proceed')]


def test_closereq(fillopers):
    sqltable.closereq('00001')
    sqltable.closereq('00003')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM request WHERE status='closed';""")
    all_result1 = cur.fetchall()
    cur.execute("""SELECT * FROM request WHERE status='proceed';""")
    all_result2 = cur.fetchall()
    conn.close()
    answerlist = [('00001', '5435345', '003', 'rajesh kutrapali', 'closed'),
            ('00003', '5435345', '003', 'rajesh kutrapale', 'closed')]
    assert all_result1 == answerlist and all_result2 == [('00002', '5435345', '002', 'rajesh kutrapalo', 'proceed')]


def test_resreq(fillopers):
    sqltable.resreq('00001')
    sqltable.resreq('00003')
    answerlist = [('00001', '5435345', '-', 'rajesh kutrapali', 'open'),
              ('00003', '5435345', '-', 'rajesh kutrapale', 'open')]

    assert sqltable.readreqlist() == answerlist


@pytest.fixture()
def indexin():
    return ['00001', '00010', '00100', '01000', '10000']


def test_rightindex(indexin):
    ints = [1, 10, 100, 1000, 10000]
    strs = []
    for i in ints:
        strs.append(sqltable.rightindex(i))
    assert strs == indexin


@pytest.fixture()
def logtable():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS log;""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS log(
                error TEXT, 
                date TEXT,
                func TEXT);""")
    conn.commit()
    conn.close()


def test_loginsert(logtable):
    sqltable.loginsert('puk', '22.15', 'srenk')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM log WHERE error='puk';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('puk', '22.15', 'srenk')


def test_sqlprevent():
    reqlist = ['"ABOB"', "'GLOB'", "'"]
    answerlist = []
    for i in reqlist:
        answerlist.append(sqltable.sqlprevent(i))
    assert answerlist == ['ABOB', "GLOB", ""]


@pytest.fixture()
def connections():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS log;""")
    conn.commit()
    cur.execute("""CREATE TABLE IF NOT EXISTS connections( 
                    userid TEXT,
                    operid TEXT);""")
    conn.commit()
    conn.close()


def test_createconnection(connections):
    sqltable.createconnection('567', '789')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM connections WHERE operid='789';""")
    one_result = cur.fetchone()
    conn.close()
    assert one_result == ('567', '789')


@pytest.fixture()
def fillconnections(connections):
    sqltable.createconnection('567', '789')
    sqltable.createconnection('5678', '7898')
    sqltable.createconnection('3567', '4789')


def test_deleteconnections(fillconnections):
    sqltable.deleteconnection('789')
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM connections;""")
    all_result = cur.fetchall()
    conn.close()
    assert all_result == [('5678', '7898'), ('3567', '4789')]


if __name__ == '__main__':
    pass
