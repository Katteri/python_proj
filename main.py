import telebot
import sqlite3
from maze_generation import get_map_cell

bot = telebot.TeleBot('7089136398:AAGiQnXmU2vNWI2kZ2VtZKM8Zjhwm_5fFwQ')
columns, rows = 6, 6
current_score = 0

# игровая клавиатура
keyboard_game = telebot.types.InlineKeyboardMarkup()
keyboard_game.row(telebot.types.InlineKeyboardButton('←', callback_data = 'left'),
				  telebot.types.InlineKeyboardButton('↑', callback_data = 'up'),
				  telebot.types.InlineKeyboardButton('↓', callback_data = 'down'),
				  telebot.types.InlineKeyboardButton('→', callback_data = 'right'))

# клавиатура главного меню
keyboard_menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
keyboard_menu.row(telebot.types.KeyboardButton('🎮 играть'))
keyboard_menu.add(telebot.types.KeyboardButton('❓ правила'),
				  telebot.types.KeyboardButton('⚙ настройки'),
				  telebot.types.KeyboardButton('📃 репозиторий'))
keyboard_menu.row(telebot.types.KeyboardButton('📊 статистика'))

# клавиатура выбора устройства
keyboard_device = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
keyboard_device.row(telebot.types.KeyboardButton('📱 телефон'),
					telebot.types.KeyboardButton('🖥 компьютер'))

# клавиатура для кнопки репозитория
github_link = 'https://github.com/Katteri/python_proj'
keyboard_link = telebot.types.InlineKeyboardMarkup()
keyboard_link.add(telebot.types.InlineKeyboardButton('здесь', url = github_link))

maps = {}

def get_map_str(map_cell, player):
	map_str = ""
	for y in range(rows * 2 - 1):
		for x in range(columns * 2 - 1):
			if map_cell[x + y * (columns * 2 - 1)]:
				map_str += "⬛"
			elif (x, y) == player:
				map_str += "🔴"
			else:
				map_str += "⬜"
		map_str += "\n"

	return map_str

# создаем таблицу и вносим данные о пользователе
def initial_table(message):
	connection = sqlite3.connect('users.sql')
	cursor = connection.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id int auto_increment primary key, username varchar(50), total_score int)')
	# проверяем есть ли запись о пользователе в бд
	info = cursor.execute('SELECT * FROM users WHERE username = ?', [message.chat.username])
	# если записи нет, создаем ее
	if info.fetchone() is None:
		cursor.execute(f'INSERT INTO users (username, total_score) VALUES (?, ?)', [message.chat.username, 0])
		bot.send_message(message.chat.id, 'Выше имя добавлено в базу данных!', reply_markup = keyboard_menu)
	connection.commit()
	cursor.close()
	connection.close()

# после игры обновляем счет игрока в таблице
def increment_score(message):
	global current_score
	connection = sqlite3.connect('users.sql')
	cursor = connection.cursor()
	cursor.execute(f'UPDATE users SET total_score = total_score + ? WHERE username LIKE ?', [current_score, message.chat.username])
	current_score = 0
	connection.commit()
	cursor.close()
	connection.close()

	bot.send_message(message.chat.id, 'Данные об игре были внесены в таблицу', reply_markup = keyboard_menu)

# стартовое сообщение
@bot.message_handler(commands=['start'])
def main(message):
	bot.send_message(message.chat.id, f'Привет, {message.chat.first_name}!\n\n▪ начать новую игру — <b>"играть"</b>\n▪ изменить размер игрового поля — <b>"настройки"</b>\n▪ узнать правила игры — <b>"правила"</b>\n▪ перейти к GitHub — <b>"репозиторий"</b>\n▪ посмотреть статистику — <b>"статистика"</b>',
				  	parse_mode = 'HTML',
				  	reply_markup = keyboard_menu)
	initial_table(message)

# запуск игры
@bot.message_handler(func=lambda message: 'играть' in message.text.lower())
def play_message(message):
	map_cell = get_map_cell(columns, rows)

	user_data = {
			'map': map_cell,
			'x': 0,
			'y': 0
		}

	maps[message.chat.id] = user_data

	bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard_game)

@bot.message_handler(func=lambda message: 'правила' in message.text.lower())
def rules(message):
	bot.send_message(message.chat.id, f'<b>Правила игры в лабиринт:</b>\n▪ дойти до нижней правой клетки, <em>не задев стены</em>',
				  	parse_mode = 'HTML',
				  	reply_markup = keyboard_menu)

# настройки, выбор размера игрового поля
@bot.message_handler(func=lambda message: 'настройки' in message.text.lower())
def settings(message):
	bot.send_message(message.chat.id, 'На каком устройстве ты играешь?', reply_markup = keyboard_device)
	bot.register_next_step_handler(message, settings)

def settings(message):
	global columns, rows
	if 'телефон' in message.text.lower():
		columns, rows = 6, 6
		bot.send_message(message.chat.id, 'Настройки изменены', reply_markup = keyboard_menu)
	elif 'компьютер' in message.text.lower():
		columns, rows = 9, 9
		bot.send_message(message.chat.id, 'Настройки изменены', reply_markup = keyboard_menu)

# ссылка на репозиторий
@bot.message_handler(func=lambda message: 'репозиторий' in message.text.lower())
def github(message):
	bot.send_message(message.chat.id, 'Репозиторий находится 🔻', reply_markup = keyboard_link)
	bot.send_message(message.chat.id, 'Спасибо за интерес к репозиторию!', reply_markup = keyboard_menu)

# вывод статистики
@bot.message_handler(func=lambda message: 'статистика' in message.text.lower())
def statistic(message):
	connection = sqlite3.connect('users.sql')
	cursor = connection.cursor()
	info = cursor.execute('SELECT * FROM users')
	if info.fetchall is None:
		bot.send_message(message.chat.id, info, reply_markup = keyboard_menu)
	else:
		bot.send_message(message.chat.id, 'Ни одна игра не была сыграна 😢', reply_markup = keyboard_menu)
	cursor.close()
	connection.close()

# функция, вызывающаяся при нажатии на кнопки игры
@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
	global current_score
	
	# получаем старые координаты
	user_data = maps[query.message.chat.id]
	new_x, new_y = user_data['x'], user_data['y']

	# определяем новые координаты
	if query.data == 'left':
		new_x -= 1
	if query.data == 'right':
		new_x += 1
	if query.data == 'up':
		new_y -= 1
	if query.data == 'down':
		new_y += 1

	# проверям возможен ли такой ход, если нет - отнимаем очки
	if new_x < 0 or new_x > 2 * columns - 2 or new_y < 0 or new_y > rows * 2 - 2:
		current_score -= 1
		return None
	if user_data['map'][new_x + new_y * (columns * 2 - 1)]:
		current_score -= 1
		return None

	user_data['x'], user_data['y'] = new_x, new_y

	# проверка на выигрыш (выигрываем, если находимся в самой правой нижней клетке)
	if new_x == columns * 2 - 2 and new_y == rows * 2 - 2:
		bot.edit_message_text( chat_id = query.message.chat.id,
							   message_id = query.message.id,
							   text = f'Вы выиграли❕\nВаш счет за игру составил {current_score} очков')
		increment_score(query.message)
		return None

	# передвигаем игрока и увеличиваем счет
	current_score += 1
	bot.edit_message_text( chat_id = query.message.chat.id,
						   message_id = query.message.id,
						   text = get_map_str(user_data['map'], (new_x, new_y)),
						   reply_markup = keyboard_game)

bot.polling(none_stop=False, interval = 0)