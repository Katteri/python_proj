import telebot
from maze_generation import get_map_cell

bot = telebot.TeleBot('secret')
columns, rows = 6, 6

# игровая клавиатура
keyboard_game = telebot.types.InlineKeyboardMarkup()
keyboard_game.row(telebot.types.InlineKeyboardButton('←', callback_data = 'left'),
				  telebot.types.InlineKeyboardButton('↑', callback_data = 'up'),
				  telebot.types.InlineKeyboardButton('↓', callback_data = 'down'),
				  telebot.types.InlineKeyboardButton('→', callback_data = 'right'))

# клавиатура главного меню
keyboard_menu = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True, one_time_keyboard=True)
keyboard_menu.row(telebot.types.KeyboardButton('играть'))
keyboard_menu.add(telebot.types.KeyboardButton('правила'),
				  telebot.types.KeyboardButton('настройки'),
				  telebot.types.KeyboardButton('репозиторий'))

# клавиатура выбора устройства
keyboard_device = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
keyboard_device.row(telebot.types.KeyboardButton('телефон'),
					telebot.types.KeyboardButton('компьютер'))

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

# стартовое сообщение
@bot.message_handler(commands=['start'])
def main(message):
	bot.send_message(message.chat.id, f'Привет, {message.chat.first_name}!\n\n- начать новую игру — <b>"играть"</b>\n- изменить размер игрового поля — <b>"настройки"</b>\n- узнать правила игры — <b>"правила"</b>\n- перейти к GitHub — <b>"репозиторий"</b>',
				  parse_mode = 'HTML',
				  reply_markup = keyboard_menu)

# запуск игры
@bot.message_handler(func=lambda message: message.text.lower() == 'играть')
def play_message(message):
	map_cell = get_map_cell(columns, rows)

	user_data = {
			'map': map_cell,
			'x': 0,
			'y': 0
		}

	maps[message.chat.id] = user_data

	bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard_game)

# ссылка на репозиторий
@bot.message_handler(func=lambda message: message.text.lower() == 'репозиторий')
def github(message):
	bot.send_message(message.chat.id, 'Репозиторий находится', reply_markup = keyboard_link)
	bot.send_message(message.chat.id, 'Спасибо за интерес к репозиторию!', reply_markup = keyboard_menu)

@bot.message_handler(func=lambda message: message.text.lower() == 'правила')
def rules(message):
	bot.send_message(message.chat.id, f'<b>Правила игры в лабиринт:</b>\n- дойти до нижней правой клетки, <em>не задев стены</em>',
				  parse_mode = 'HTML',
				  reply_markup = keyboard_menu)

# настройки, выбор размера игрового поля
@bot.message_handler(func=lambda message: message.text.lower() == 'настройки')
def settings(message):
	bot.send_message(message.chat.id, 'На каком устройстве ты играешь?', reply_markup = keyboard_device)
	bot.register_next_step_handler(message, settings)

def settings(message):
	global columns, rows
	if message.text.lower() == 'телефон':
		columns, rows = 6, 6
		bot.send_message(message.chat.id, 'Настройки изменены', reply_markup = keyboard_menu)
	elif message.text.lower() == 'компьютер':
		columns, rows = 9, 9
		bot.send_message(message.chat.id, 'Настройки изменены', reply_markup = keyboard_menu)

# функция, вызывающаяся при нажатии на кнопки игры
@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
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

	# проверям возможен ли такой ход
	if new_x < 0 or new_x > 2 * columns - 2 or new_y < 0 or new_y > rows * 2 - 2:
		return None
	if user_data['map'][new_x + new_y * (columns * 2 - 1)]:
		return None

	user_data['x'], user_data['y'] = new_x, new_y

	# проверка на выигрыш (выигрываем, если находимся в самой правой нижней клетке)
	if new_x == columns * 2 - 2 and new_y == rows * 2 - 2:
		bot.edit_message_text( chat_id=query.message.chat.id,
							   message_id=query.message.id,
							   text="Вы выиграли",
							   reply_markup=keyboard_menu)
		return None

	# изменяем сообщение
	bot.edit_message_text( chat_id=query.message.chat.id,
						   message_id=query.message.id,
						   text=get_map_str(user_data['map'], (new_x, new_y)),
						   reply_markup=keyboard_game)

bot.polling(none_stop=False, interval=0)