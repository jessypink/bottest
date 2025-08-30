from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# Хранение игроков
players = {}

# Начало игры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    players[user_id] = {
        "hp": 20,
        "gold": 0,
        "potions": 1,
        "stage": "intro"
    }

    await update.message.reply_text(
        "🌌 Ты очнулся у входа в древнее подземелье.\n"
        "Говорят, внутри хранится сокровище, но его охраняет тёмный владыка...\n"
        "Что будешь делать?",
        reply_markup=choices_intro()
    )

# Главное меню выбора
def choices_intro():
    keyboard = [
        [InlineKeyboardButton("⚔ Войти в подземелье", callback_data="enter")],
        [InlineKeyboardButton("🏃 Уйти домой", callback_data="leave")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Меню боёв
def choices_battle():
    keyboard = [
        [InlineKeyboardButton("🗡 Атаковать", callback_data="attack")],
        [InlineKeyboardButton("🍷 Использовать зелье", callback_data="potion")],
        [InlineKeyboardButton("🏃 Сбежать", callback_data="run")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Кнопки после победы
def choices_after_battle():
    keyboard = [
        [InlineKeyboardButton("➡ Дальше", callback_data="next_stage")],
        [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    player = players.get(user_id)

    if not player:
        await query.edit_message_text("Сначала напиши /start")
        return

    # --- ВСТУПЛЕНИЕ ---
    if query.data == "enter" and player["stage"] == "intro":
        player["stage"] = "monster1"
        await query.edit_message_text(
            "Ты заходишь внутрь... 👣\n"
            "Из тени выпрыгивает первый монстр — Гоблин!",
            reply_markup=choices_battle()
        )
        player["monster_hp"] = 10

    elif query.data == "leave" and player["stage"] == "intro":
        players.pop(user_id)
        await query.edit_message_text("Ты решил не рисковать и ушёл домой. 🏡 Конец игры.")

    # --- БОЙ ---
    elif query.data == "attack":
        dmg = random.randint(3, 6)
        player["monster_hp"] -= dmg
        if player["monster_hp"] <= 0:
            player["gold"] += 5
            text = f"🎉 Ты победил врага и получил 5 золота!\nТекущие HP: {player['hp']}"
            player["stage"] = "after_battle"
            await query.edit_message_text(text, reply_markup=choices_after_battle())
        else:
            # Монстр бьет
            mdmg = random.randint(2, 5)
            player["hp"] -= mdmg
            if player["hp"] <= 0:
                players.pop(user_id)
                await query.edit_message_text("☠️ Монстр оказался сильнее... Ты погиб.")
            else:
                await query.edit_message_text(
                    f"Ты ударил монстра на {dmg} урона!\n"
                    f"Монстр атаковал и снял {mdmg} HP.\n"
                    f"Твои HP: {player['hp']} | HP монстра: {player['monster_hp']}",
                    reply_markup=choices_battle()
                )

    elif query.data == "potion":
        if player["potions"] > 0:
            player["hp"] = min(20, player["hp"] + 8)
            player["potions"] -= 1
            await query.edit_message_text(
                f"🍷 Ты выпил зелье. HP: {player['hp']} | Зелий осталось: {player['potions']}",
                reply_markup=choices_battle()
            )
        else:
            await query.edit_message_text("❌ У тебя нет зелий!", reply_markup=choices_battle())

    elif query.data == "run":
        player["stage"] = "intro"
        await query.edit_message_text("Ты сбежал обратно ко входу. 🚪", reply_markup=choices_intro())

    # --- ПОСЛЕ БИТВЫ ---
    elif query.data == "next_stage" and player["stage"] == "after_battle":
        player["stage"] = "boss"
        player["monster_hp"] = 20
        await query.edit_message_text(
            "Ты идёшь дальше по тёмному коридору... 🔦\n"
            "Внезапно воздух становится тяжёлым. Перед тобой появляется ТЁМНЫЙ ВЛАДЫКА! 👹",
            reply_markup=choices_battle()
        )

    elif query.data == "inventory":
        await query.edit_message_text(
            f"🎒 Инвентарь:\nHP: {player['hp']}\nЗолото: {player['gold']}\nЗелья: {player['potions']}",
            reply_markup=choices_after_battle()
        )

    # --- ФИНАЛ ---
    if player.get("stage") == "boss" and player["hp"] > 0 and player["monster_hp"] <= 0:
        await query.edit_message_text(
            "🔥 Ты победил Тёмного Владыку!\n"
            "В сокровищнице ты находишь сундук с золотом и артефакт.\n"
            "🌟 Поздравляем, герой! Ты прошёл подземелье!",
        )
        players.pop(user_id)


if __name__ == "__main__":
    TOKEN = "5510933125:AAFpVK0ndCpCh548sdx02-Bx0BcUHz8iJI4"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("RPG-бот с сюжетом запущен…")
    app.run_polling()
