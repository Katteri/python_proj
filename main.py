import telebot
import sqlite3
import time
from maze_generation import get_map_cell

bot = telebot.TeleBot("secret")


class game_settings:
    columns, rows = 6, 6
    max_time = 300
    start_time = 0
    penalty = 0
    current_score = 0

    def update_columns(columns):
        game_settings.columns = columns

    def update_rows(rows):
        game_settings.rows = rows

    def update_max_time(max_time):
        game_settings.max_time = max_time

    def update_start_time(start_time):
        game_settings.start_time = start_time

    def update_penalty(penalty):
        game_settings.penalty = penalty

    def update_current_score(current_score):
        game_settings.current_score = current_score


# игровая клавиатура
keyboard_game = telebot.types.InlineKeyboardMarkup()
keyboard_game.row(
    telebot.types.InlineKeyboardButton("←", callback_data="left"),
    telebot.types.InlineKeyboardButton("↑", callback_data="up"),
    telebot.types.InlineKeyboardButton("↓", callback_data="down"),
    telebot.types.InlineKeyboardButton("→", callback_data="right"),
)

# клавиатура главного меню
keyboard_menu = telebot.types.ReplyKeyboardMarkup(
    row_width=3, resize_keyboard=True, one_time_keyboard=True
)
keyboard_menu.row(telebot.types.KeyboardButton("🎮 играть"))
keyboard_menu.add(
    telebot.types.KeyboardButton("❓ правила"),
    telebot.types.KeyboardButton("⚙ настройки"),
    telebot.types.KeyboardButton("📃 репозиторий"),
)
keyboard_menu.row(telebot.types.KeyboardButton("📊 статистика"))

# клавиатура выбора устройства
keyboard_device = telebot.types.ReplyKeyboardMarkup(
    row_width=1, resize_keyboard=True, one_time_keyboard=True
)
keyboard_device.row(
    telebot.types.KeyboardButton("📱 телефон"),
    telebot.types.KeyboardButton("🖥 компьютер"),
)

# клавиатура для кнопки репозитория
github_link = "https://github.com/Katteri/python_proj"
keyboard_link = telebot.types.InlineKeyboardMarkup()
keyboard_link.add(telebot.types.InlineKeyboardButton("здесь", url=github_link))

maps = {}


def get_map_str(map_cell, player):
    map_str = ""
    for y in range(game_settings.rows * 2 - 1):
        for x in range(game_settings.columns * 2 - 1):
            if map_cell[x + y * (game_settings.columns * 2 - 1)]:
                map_str += "⬛"
            elif (x, y) == player:
                map_str += "🔴"
            else:
                map_str += "⬜"
        map_str += "\n"

    return map_str


# создаем таблицу и вносим данные о пользователе
def initial_table(message):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username varchar(50), total_score int)"
    )
    # проверяем есть ли запись о пользователе в бд
    info = cursor.execute(
        "SELECT * FROM users WHERE username = ?", [message.chat.username]
    )
    # если записи нет, создаем ее
    if info.fetchone() is None:
        cursor.execute(
            f"INSERT INTO users (username, total_score) VALUES (?, ?)",
            [message.chat.username, 0],
        )
        bot.send_message(
            message.chat.id,
            "Выше имя добавлено в базу данных!",
            reply_markup=keyboard_menu,
        )
    connection.commit()
    cursor.close()
    connection.close()


# после игры обновляем счет игрока в таблице
def increment_score(message):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute(
        f"UPDATE users SET total_score = total_score + ? WHERE username LIKE ?",
        [game_settings.current_score, message.chat.username],
    )
    game_settings.update_current_score(0)
    connection.commit()
    cursor.close()
    connection.close()

    bot.send_message(
        message.chat.id,
        "Данные об игре были внесены в таблицу",
        reply_markup=keyboard_menu,
    )


# стартовое сообщение
@bot.message_handler(commands=["start"])
def main(message):
    bot.send_message(
        message.chat.id,
        f'Привет, {message.chat.first_name}!\n\n▪ начать новую игру — <b>"играть"</b>\n▪ изменить размер игрового поля — <b>"настройки"</b>\n▪ узнать правила игры — <b>"правила"</b>\n▪ перейти к GitHub — <b>"репозиторий"</b>\n▪ посмотреть статистику — <b>"статистика"</b>',
        parse_mode="HTML",
        reply_markup=keyboard_menu,
    )
    initial_table(message)


# запуск игры
@bot.message_handler(func=lambda message: "играть" in message.text.lower())
def play_message(message):
    game_settings.update_start_time(time.time())

    map_cell = get_map_cell(game_settings.columns, game_settings.rows)

    user_data = {"map": map_cell, "x": 0, "y": 0}

    maps[message.chat.id] = user_data

    bot.send_message(
        message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard_game
    )


@bot.message_handler(func=lambda message: "правила" in message.text.lower())
def rules(message):
    bot.send_message(
        message.chat.id,
        f"<b>Правила игры в лабиринт:</b>\n▪ как можно быстрее дойти до правой нижней клетки, <em>не задев стены</em>",
        parse_mode="HTML",
        reply_markup=keyboard_menu,
    )


# настройки, выбор размера игрового поля
@bot.message_handler(func=lambda message: "настройки" in message.text.lower())
def settings(message):
    bot.send_message(
        message.chat.id, "На каком устройстве ты играешь?", reply_markup=keyboard_device
    )
    bot.register_next_step_handler(message, settings)


def settings(message):
    if "телефон" in message.text.lower():
        game_settings.update_columns(6)
        game_settings.update_rows(6)
        game_settings.update_max_time(300)
    elif "компьютер" in message.text.lower():
        game_settings.update_columns(9)
        game_settings.update_rows(9)
        game_settings.update_max_time(600)
    bot.send_message(message.chat.id, "Настройки изменены", reply_markup=keyboard_menu)


# ссылка на репозиторий
@bot.message_handler(func=lambda message: "репозиторий" in message.text.lower())
def github(message):
    bot.send_message(
        message.chat.id, "Репозиторий находится 🔻", reply_markup=keyboard_link
    )
    bot.send_message(
        message.chat.id, "Спасибо за интерес к репозиторию!", reply_markup=keyboard_menu
    )


# вывод статистики
@bot.message_handler(func=lambda message: "статистика" in message.text.lower())
def statistic(message):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    # берем только значение очков у пользователя. Так как нам возвращают кортеж, берем первое значение
    total_score = cursor.execute(
        "SELECT total_score FROM users WHERE username = ?", [message.chat.username]
    ).fetchone()[0]
    if total_score == 0:
        bot.send_message(
            message.chat.id,
            "Ни одна игра не была сыграна 😢",
            reply_markup=keyboard_menu,
        )
    else:
        # извлекаем топ 5 пользователей
        stat = cursor.execute(
            "SELECT DENSE_RANK() OVER(ORDER BY total_score DESC) AS rank, total_score, username FROM users ORDER BY rank LIMIT 5"
        ).fetchall()
        # считаем табуляцию для очков
        max_lengths = [max(len(str(item)) for item in col) for col in stat]

        # записываем статистику в строку для последующего вывода сообщения
        s = "<b>ТОП 5 игроков</b>\n\n"
        header = ("место", "очки", "имя")
        for i, (item, length) in enumerate(zip(header, max_lengths)):
            s += f"{str(item):<{length}} "
        s += "\n"

        for row in stat:
            for i, (item, length) in enumerate(zip(row, max_lengths)):
                s += f"{str(item):<{length}} "
                if i == len(row) - 1:
                    s += "\n"

        # считаем собственный ранк пользователя
        user_rank = cursor.execute(
            "SELECT rank, total_score FROM (SELECT DENSE_RANK() OVER(ORDER BY total_score DESC) AS rank, username, total_score FROM users) WHERE username = ?",
            [message.chat.username],
        ).fetchone()[0]
        s += f"\n\nВаше место в топе: <b>{user_rank}</b>\nСумма ваших очков за все игры: <b>{total_score}</b>"
        bot.send_message(
            message.chat.id, s, parse_mode="HTML", reply_markup=keyboard_menu
        )
    cursor.close()
    connection.close()


# функция, вызывающаяся при нажатии на кнопки игры
@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
    # получаем старые координаты
    user_data = maps[query.message.chat.id]
    new_x, new_y = user_data["x"], user_data["y"]

    # определяем новые координаты
    if query.data == "left":
        new_x -= 1
    if query.data == "right":
        new_x += 1
    if query.data == "up":
        new_y -= 1
    if query.data == "down":
        new_y += 1

    # проверям возможен ли такой ход, если нет - отнимаем очки
    if (
        new_x < 0
        or new_x > 2 * game_settings.columns - 2
        or new_y < 0
        or new_y > game_settings.rows * 2 - 2
    ):
        game_settings.update_penalty(game_settings.penalty + 1)
        return None
    if user_data["map"][new_x + new_y * (game_settings.columns * 2 - 1)]:
        game_settings.update_penalty(game_settings.penalty + 1)
        return None

    user_data["x"], user_data["y"] = new_x, new_y

    # проверка на выигрыш (выигрываем, если находимся в самой правой нижней клетке)
    if new_x == game_settings.columns * 2 - 2 and new_y == game_settings.rows * 2 - 2:
        # максимум играем 5 минут, из них вычитаем сколько время играли и штрафные очки, все это делим на 10
        game_settings.update_current_score(
            (
                game_settings.max_time
                - round(time.time() - game_settings.start_time)
                - game_settings.penalty * 10
            )
            // 10
        )
        if game_settings.current_score > 0:
            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                text=f"Вы выиграли❗\nВаш счет за игру: {game_settings.current_score} ✨",
            )
        else:
            bot.edit_message_text(
                chat_id=query.message.chat.id,
                message_id=query.message.id,
                text=f"Вы проиграли с счетом {game_settings.current_score} 😭",
            )
        increment_score(query.message)
        return None

    # передвигаем игрока
    bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.id,
        text=get_map_str(user_data["map"], (new_x, new_y)),
        reply_markup=keyboard_game,
    )


bot.polling(none_stop=False, interval=0)
