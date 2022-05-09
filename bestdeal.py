import telebot

token = '1926132610:AAEk3BQiM1RTWldwZzzCNH9dYq6R0EsHgbI'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['bestdeal'])
def bestdeal(message):
    bot.send_message(message.from_user.id, 'Функция в разработке.')