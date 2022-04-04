import telebot
import lowprice
import highprice
import bestdeal
import history
import hotels_api


token = '1926132610:AAEk3BQiM1RTWldwZzzCNH9dYq6R0EsHgbI'
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=['text'])
def get_message(message):
    if message.text == "Привет" or message.text == "/hello_world":
        bot.send_message(message.from_user.id, f"Привет, {message.from_user.first_name}")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши 'Привет' или /hello_world")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=0)
