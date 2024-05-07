import telebot
from maze_generation import get_map_cell

bot = telebot.TeleBot('7089136398:AAGiQnXmU2vNWI2kZ2VtZKM8Zjhwm_5fFwQ')
columns, rows = 6, 6

keyboard = telebot.types.InlineKeyboardMarkup()
keyboard.row( telebot.types.InlineKeyboardButton('←', callback_data='left'),
			  telebot.types.InlineKeyboardButton('↑', callback_data='up'),
			  telebot.types.InlineKeyboardButton('↓', callback_data='down'),
			  telebot.types.InlineKeyboardButton('→', callback_data='right') )

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

@bot.message_handler(commands=['play'])
def play_message(message):
	map_cell = get_map_cell(columns, rows)

	user_data = {
		'map': map_cell,
		'x': 0,
		'y': 0
	}

	maps[message.chat.id] = user_data

	bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0)), reply_markup=keyboard)

# функция, вызывающаяся при нажатии на кнопку
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
							   text="Вы выиграли" )
		return None

	# изменяем сообщение
	bot.edit_message_text( chat_id=query.message.chat.id,
						   message_id=query.message.id,
						   text=get_map_str(user_data['map'], (new_x, new_y)),
						   reply_markup=keyboard )

bot.polling(none_stop=False, interval=0)