from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Команда start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE)
    await update.message.reply_text("Привет! Я простой эхо-бот. Пиши что угодно, и я повторю.")

# Основной обработчик сообщений
async def echo(update Update, context ContextTypes.DEFAULT_TYPE)
    user_text = update.message.text
    await update.message.reply_text(user_text)

if __name__ == __main__
    TOKEN = 5510933125:AAFpVK0ndCpCh548sdx02-Bx0BcUHz8iJI4  # - вставь сюда токен своего бота
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler(start, start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print(Бот запущен...)
    app.run_polling()


