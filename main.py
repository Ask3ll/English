import database
import telebot
from time import sleep
from _token_ import _token
me = 1737599584
bot = telebot.TeleBot(_token)
db = database.Database()
ready = True
report = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in list(report.keys()):
        report[message.chat.id] = []
    db.exec(f"SELECT * FROM users WHERE telegram_id={message.chat.id}")
    user = db.all()
    markup = telebot.types.ReplyKeyboardMarkup()
    btn = telebot.types.KeyboardButton("✅ Добавить слово")
    markup.add(btn)
    btn = telebot.types.KeyboardButton("🗒️ Посмотреть все слова")
    markup.add(btn)
    btn = telebot.types.KeyboardButton("📒 Начать тест")
    markup.add(btn)
    btn = telebot.types.KeyboardButton("🧐 Статистика")
    markup.add(btn)
    print(user)
    if user:
        pass
    else:
        db.exec(f"INSERT INTO users (telegram_id, correct, incorrect, total) VALUES ({message.chat.id}, 0, 0, 0)", True)
    bot.send_message(message.chat.id, f'''
Добро пожаловать {message.from_user.first_name}! 
Этот бот поможет вам изучать английский язык. 
Вы можете добавлять новые слова и фразы для изучения, а также проходить тесты для проверки своих знаний. 
Начните, добавив первые слова или перейдите сразу к тестированию. Удачи в изучении английского!''', reply_markup=markup)


def _question(message, id):
        global ready
        if str(id) not in report[message.chat.id]:
                db.exec(f"SELECT translate FROM questions WHERE id = {id}")
                trnsl = db.one()[0]
                if trnsl == message.text:
                        bot.send_message(message.chat.id, "Правильно!")
                        db.exec(f"UPDATE users SET correct = correct + 1 WHERE telegram_id = {message.chat.id}", True)
                        ready = False
                else:
                        bot.send_message(message.chat.id, "Неправильно!")
                        db.exec(f"UPDATE users SET incorrect = incorrect + 1 WHERE telegram_id = {message.chat.id}", True)
                        ready = False


@bot.message_handler(commands=['test'])
def test(message):
    global ready
    db.exec(f"SELECT * FROM users WHERE telegram_id={message.chat.id}")
    user = db.all()
    if user:
        if message.chat.id not in list(report.keys()):
            report[message.chat.id] = []
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text=f"Только свои слова", callback_data=f"regular")
        markup.add(button)
        button = telebot.types.InlineKeyboardButton(text=f"Все слова", callback_data=f"all")
        markup.add(button)
        bot.send_message(message.chat.id, "Какой тест вы хотите пройти?", reply_markup=markup)


def adder2(message, text):
    db.exec(
        f"INSERT INTO questions (telegram_id, answer, translate) VALUES({message.chat.id}, '{text}', '{message.text}')",
        True)
    db.exec(f"UPDATE users SET total = total + 1 WHERE telegram_id = {message.chat.id}", True)
    bot.send_message(message.chat.id, "Слово успешно добавлено")


def adder(message):
    bot.send_message(message.chat.id, "А теперь введите его перевод")
    bot.register_next_step_handler(message, adder2, message.text)


def paginate_list(lst, page_size):
    return [lst[i:i + page_size] for i in range(0, len(lst), page_size)]


def redw(message, id):
    db.exec(f"UPDATE questions SET answer = '{message.text}' WHERE id = {id}", True)
    bot.send_message(message.chat.id, "Слово успешно изменено!")


def redq(message, id):
    db.exec(f"UPDATE questions SET translate = '{message.text}' WHERE id = {id}", True)
    bot.send_message(message.chat.id, "Перевод успешно изменен!")


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data[:4] == "redq":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        db.exec(f"SELECT answer, translate FROM questions WHERE id = {call.data[5:]}")
        questions = db.one()
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text=f"Слово - {questions[0]}",
                                                    callback_data=f"redw {call.data[5:]}")
        markup.add(button)
        button = telebot.types.InlineKeyboardButton(text=f"Перевод - {questions[1]}",
                                                    callback_data=f"redt {call.data[5:]}")
        markup.add(button)
        button = telebot.types.InlineKeyboardButton(text="Удалить оба слова", callback_data=f"delq {call.data[5:]}")
        markup.add(button)
        bot.send_message(call.from_user.id, "Нажмите на пункт для редактирования", reply_markup=markup)
    elif call.data[:4] == "delq":
        db.exec(f"DELETE FROM questions WHERE id = {call.data[5:]}", True)
        bot.edit_message_text(chat_id=call.message.chat.id, text="Слово успешно удалено!", message_id=call.message.id)

    elif call.data[:4] == "redw":
        markup = telebot.types.ReplyKeyboardMarkup()
        bot.send_message(call.from_user.id, "Введите новое слово", reply_markup=markup)
        bot.delete_message(message_id=call.message.id, chat_id=call.message.chat.id)
        bot.register_next_step_handler(call.message, redw, call.data[5:])
    elif call.data[:4] == "redt":
        markup = telebot.types.ReplyKeyboardMarkup()
        bot.send_message(call.from_user.id, "Введите новый перевод", reply_markup=markup)
        bot.delete_message(message_id=call.message.id, chat_id=call.message.chat.id)
        bot.register_next_step_handler(call.message, redq, call.data[5:])
    elif call.data[:4] == "back":
        db.exec(f"SELECT id, answer, translate FROM questions WHERE telegram_id = {call.message.chat.id}")
        page = int(call.data[5:])
        questions = db.all()
        markup = telebot.types.InlineKeyboardMarkup()
        questions = paginate_list(questions, 5)
        if questions == []:
            q = []
        else:
            q = questions[page]
        for i in q:
            button = telebot.types.InlineKeyboardButton(text=f"{i[1]} - {i[2]}",
                                                        callback_data=f"redq {i[0]}")
            markup.add(button)
        if page == 0:
            button = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
            markup.add(button)
        else:
            button = telebot.types.InlineKeyboardButton(text=f"⬅️", callback_data=f"back {page - 1}")
            button2 = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
            markup.add(button, button2)
        if questions == []:
            bot.send_message(call.message.chat.id, "Слов нет!")
        else:
            bot.send_message(call.message.chat.id, f"Выберите слово\n\n _Страница {page + 1}/{len(questions)}_",
                             reply_markup=markup, parse_mode="markdown")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    elif call.data[:7] == "forward":
        db.exec(f"SELECT id, answer, translate FROM questions WHERE telegram_id = {call.message.chat.id}")
        page = int(call.data[8:])
        questions = db.all()
        markup = telebot.types.InlineKeyboardMarkup()
        questions = paginate_list(questions, 5)
        q = questions[page]
        for i in q:
            button = telebot.types.InlineKeyboardButton(text=f"{i[1]} - {i[2]}",
                                                        callback_data=f"redq {i[0]}")
            markup.add(button)
        if page == 0:
            button = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
            markup.add(button)
        else:
            button = telebot.types.InlineKeyboardButton(text=f"⬅️", callback_data=f"back {page - 1}")
            button2 = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
            markup.add(button, button2)
        if questions == []:
            bot.send_message(call.message.chat.id, "Слов нет!")
        else:
            bot.send_message(call.message.chat.id, f"Выберите слово\n\n _Страница {page + 1}/{len(questions)}_",
                             reply_markup=markup, parse_mode="markdown")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    elif call.data[:7] == "regular":
        global ready
        db.exec(f"SELECT total FROM users WHERE telegram_id = {call.message.chat.id}")
        total = db.one()[0]
        if total < 10:
            db.exec(
                f"SELECT answer, translate, id FROM questions WHERE telegram_id = {call.message.chat.id} ORDER BY RANDOM() LIMIT {total}")
        else:
            db.exec(
                f"SELECT answer, translate, id FROM questions WHERE telegram_id = {call.message.chat.id} ORDER BY RANDOM() LIMIT 10")
        questions = db.all()
        db.exec(f"SELECT correct, incorrect FROM users WHERE telegram_id = {call.message.chat.id}")
        stat = db.one()
        for i in questions:
            bot.send_message(call.message.chat.id, f"{i[0]}")
            bot.register_next_step_handler(call.message, _question, i[2])
            while ready:
                sleep(1)
            ready = True
        db.exec(f"SELECT correct, incorrect FROM users WHERE telegram_id = {call.message.chat.id}")
        stat2 = db.one()
        bot.send_message(call.message.chat.id,f"Тест завершен! {stat2[0] - stat[0]} Правильных ответов, {stat2[1] - stat[1]} Неправильных ответов")
    elif call.data[:3] == "all":
        db.exec(
            f"SELECT answer, translate, id FROM questions WHERE telegram_id != {call.message.chat.id} ORDER BY RANDOM() LIMIT 10")
        questions = db.all()
        db.exec(f"SELECT correct, incorrect FROM users WHERE telegram_id = {call.message.chat.id}")
        stat = db.one()


        b = 0
        for i in questions:
            b+=1
            markup = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text=f"Пожаловатся на слово", callback_data=f"report {i[2]}")
            markup.add(button)
            bot.send_message(call.message.chat.id, f"""
_Вопрос {b} из 10_

{i[0]}

_Введите перевод этого слова_
""", reply_markup=markup, parse_mode="markdown")
            bot.register_next_step_handler(call.message, _question, i[2])
            while ready:
                sleep(1)
            ready = True
        db.exec(f"SELECT correct, incorrect FROM users WHERE telegram_id = {call.message.chat.id}")
        stat2 = db.one()
        bot.send_message(call.message.chat.id, f"Тест завершен! {stat2[0] - stat[0]} Правильных ответов, {stat2[1] - stat[1]} Неправильных ответов")
    elif call.data[:6] == "report":
        if call.message.chat.id not in list(report.keys()):
            report[call.message.chat.id] = []
        bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)
        report[call.from_user.id].append(call.data[7:])
        print(call.data)
        bot.send_message(me, f"{call.from_user.first_name}({call.from_user.id}) пожаловался на вопрос - {call.data[7:]}")
        bot.send_message(call.from_user.id, "Спасибо за обращение! Ваш запрос будет отправлен администрации на рассмотрение")
        ready = False

@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == "✅ Добавить слово":
        bot.send_message(message.chat.id, "Отправьте слово которое нужно добавить")
        bot.register_next_step_handler(message, adder)
    elif message.text == "🗒️ Посмотреть все слова":
        db.exec(f"SELECT id, answer, translate FROM questions WHERE telegram_id = {message.chat.id}")
        page = 0
        questions = db.all()
        if questions != []:
            markup = telebot.types.InlineKeyboardMarkup()
            questions = paginate_list(questions, 5)
            print(questions, page)
            q = questions[page]
            for i in q:
                button = telebot.types.InlineKeyboardButton(text=f"{i[1]} - {i[2]}", callback_data=f"redq {i[0]}")
                markup.add(button)
            if page == 0:
                button = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
                markup.add(button)
            else:
                button = telebot.types.InlineKeyboardButton(text=f"⬅️", callback_data=f"back {page - 1}")
                button2 = telebot.types.InlineKeyboardButton(text=f"➡️", callback_data=f"forward {page + 1}")
                markup.add(button, button2)
            if questions == []:
                bot.send_message(message.chat.id, "Слов нет!")
            else:
                bot.send_message(message.chat.id, f"Выберите слово\n\n _Страница {page + 1}/{len(questions)}_",
                                 reply_markup=markup, parse_mode="markdown")
        else:
            bot.send_message(message.chat.id, "Слов нет!")
    elif message.text == "🧐 Статистика":
        db.exec(f"SELECT correct, incorrect FROM users WHERE telegram_id = {message.chat.id}")
        stat = db.one()
        bot.send_message(message.chat.id, f"Кол-во правильных ответов - {stat[0]}, кол-во неправильных - {stat[1]}")
    elif message.text == "📒 Начать тест":
        if message.chat.id not in list(report.keys()):
            report[message.chat.id] = []
        test(message)

bot.infinity_polling()