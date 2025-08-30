from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import speech_recognition as sr
import os

# Папка для временных файлов
TEMP_DIR = r"C:\CloudTG"
os.makedirs(TEMP_DIR, exist_ok=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот TTS/STT.\n"
        "- Отправь текст, и я превращу его в аудио.\n"
        "- Отправь голосовое сообщение, и я расшифрую его в текст."
    )

# Превращаем текст в речь
async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    tts = gTTS(text=user_text, lang='ru')
    file_path = os.path.join(TEMP_DIR, "tts.mp3")
    tts.save(file_path)
    await update.message.reply_audio(open(file_path, 'rb'))
    os.remove(file_path)

# Распознаём голос в текст
async def speech_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = await update.message.voice.get_file()
    file_path = os.path.join(TEMP_DIR, "voice.ogg")
    await voice.download_to_drive(file_path)

    # Конвертируем OGG в WAV через ffmpeg (нужно установить ffmpeg)
    wav_path = os.path.join(TEMP_DIR, "voice.wav")
    os.system(f'ffmpeg -i "{file_path}" "{wav_path}" -y')
    os.remove(file_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    os.remove(wav_path)

    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        await update.message.reply_text(f"Я распознал: {text}")
    except sr.UnknownValueError:
        await update.message.reply_text("Не удалось распознать речь.")
    except sr.RequestError:
        await update.message.reply_text("Ошибка сервиса распознавания.")

if __name__ == "__main__":
    TOKEN = "5510933125:AAFpVK0ndCpCh548sdx02-Bx0BcUHz8iJI4"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))
    app.add_handler(MessageHandler(filters.VOICE, speech_to_text))

    print("Бот запущен…")
    app.run_polling()
