import telebot

import schedule
import time
import threading
import random
import os

from typing import Tuple, Set
from itertools import zip_longest


token = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(token)

chat_id = None
footballers = set()
not_footballers = set()
footballers_test = {'Добромир', 'Святослав', 'Алексей', 'Артем', 'Сергей', 'Вадим', 'Александр'}


def job():
    schedule.every().monday.at("12:00").do(send_wednesday_poll)
    schedule.every().thursday.at("09:00").do(clear_footballers)

    while True:
        schedule.run_pending()
        time.sleep(60)


def start_scheduler():
    thread = threading.Thread(target=job)
    thread.start()


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    message_text = message.text.lower()
    if message_text.startswith('привет, бот!'):
        global chat_id
        chat_id = message.chat.id
        bot.send_message(message.chat.id, "Привет ✌️")
    if message_text == 'подели тест':
        divide_and_send_message(True)
    if message_text == 'подели':
        if len(footballers) == 0 and len(not_footballers) == 0:
            bot.send_message(message.chat.id, "Никто ещё не проголосовал 😬️")
        elif len(footballers) == 0:
            bot.send_message(message.chat.id, "️Никто ещё не решился 😁")
        elif len(footballers) == 1:
            bot.send_message(message.chat.id, "️Решился только один! Как его разделить на 2 команды? 😁")
        else:
            divide_and_send_message(False)
    if message_text == 'запускай':
        send_wednesday_poll()
    if message_text == 'очисти голоса':
        clear_footballers()
        bot.send_message(message.chat.id, "Сейчас сделаем 👌🏼")


@bot.poll_answer_handler(func=lambda answer: True)
def handle_poll_answer(answer):
    player_name = str()
    if answer.user.username is not None:
        player_name = answer.user.username
    elif answer.user.first_name is not None:
        player_name = answer.user.first_name
    elif answer.user.last_name is not None:
        player_name = answer.user.last_name
    else:
        player_name = answer.user.id

    player_name = player_name[:12] if len(player_name) > 12 else player_name

    if answer.option_ids == [0]:
        footballers.add(player_name)
    elif answer.option_ids == [1]:
        footballers.add(player_name)
        footballers.add('+1 ' + player_name)
    elif answer.option_ids == [2]:
        not_footballers.add(player_name)
    elif answer.option_ids == []:
        if player_name in footballers:
            footballers.remove(player_name)
        if player_name in not_footballers:
            not_footballers.remove(player_name)
        if '+1 ' + player_name in footballers:
            footballers.remove('+1 ' + player_name)
        if '+1 ' + player_name in not_footballers:
            not_footballers.remove('+1 ' + player_name)


def send_wednesday_poll():
    global chat_id
    if chat_id is not None:
        poll_message = bot.send_poll(chat_id, 'Играешь в среду?', ['Да', 'Да, со мной +1', 'Нет'], is_anonymous=False)
        bot.pin_chat_message(chat_id, poll_message.message_id)


def clear_footballers():
    global footballers, not_footballers
    footballers.clear()
    not_footballers.clear()


def divide_into_teams(is_test)-> Tuple[Set[str], Set[str]]:
    players = set(footballers_test) if is_test else set(footballers)
    team_1 = set()
    team_2 = set()
    for i in range(len(players)):
        player = random.choice(list(players))
        players.remove(player)
        if i == 0 or i % 2 == 0:
           team_1.add(player)
        else:
           team_2.add(player)
    return team_1, team_2


def divide_and_send_message(is_test):
    team_1, team_2 = divide_into_teams(is_test)
    message_teams = make_message_teams(team_1, team_2)
    bot.send_message(chat_id, text=message_teams, parse_mode='HTML')


def make_message_teams(team_1, team_2) -> str:
    team_1=list(team_1)
    team_2=list(team_2)

    message = "<pre>\n" + "🦺{:<20}👕{:<20}\n".format(' Команда 1', ' Команда 2')
    for player1, player2 in zip_longest(team_1, team_2, fillvalue=''):
        prefix_1 = '•' if player1 != '' else ''
        prefix_2 = '•' if player2 != '' else ''
        message += (prefix_1 + '{:<20} ' + prefix_2 + '{:<20}\n').format(player1, player2)
    message += "</pre>"

    return message


if __name__ == '__main__':
    start_scheduler()
    bot.infinity_polling()