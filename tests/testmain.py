import main
import sqltable
import pytest
import telebot
from telebot import types


@pytest.fixture()
def msg():
    chat = types.Chat('56787656', 'private')
    user = types.User('56787656', False, 'Egor')
    message = types.Message(int, user, 1718, chat)
    return message


def


if __name__ == '__main__':
    pass