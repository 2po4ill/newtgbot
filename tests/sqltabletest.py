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
def request():
    conn = sqlite3.connect('tgbot.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS request(
        fio TEXT, 
        mail TEXT,
        numbers TEXT);""")
    conn.commit()
    conn.close()


def test_insertreq():
    pass


if __name__ == '__main__':
    pass
