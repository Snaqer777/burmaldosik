import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from minecraft_api import get_server_status

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN получен: {bool(BOT_TOKEN)}")
print(f"TOKEN начинается с: {str(BOT_TOKEN)[:10] if BOT_TOKEN else 'ПУСТО'}")

MC_HOST = "wise-beings.gl.joinmc.link"  # ← ваш сервер
MC_PORT = 25565
MC_BEDROCK = False


def escape(text: str) -> str:
    """Экранирует спецсимволы для HTML"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_status(data: dict) -> str:
    if not data["online"]:
        return (
            "🔴 <b>Сервер оффлайн</b>\n"
            f"Ошибка: <code>{escape(data.get('error', 'неизвестно'))}</code>"
        )

    players_list = ""
    if data["players"]:
        names = "\n".join(f"  • {escape(name)}" for name in data["players"])
        players_list = f"\n\n👥 <b>Игроки онлайн:</b>\n{names}"
    elif data["players_online"] > 0:
        players_list = "\n\n👥 <b>Игроки онлайн</b> (список недоступен)"

    return (
        f"🟢 <b>Сервер онлайн</b>\n\n"
        f"📋 <b>MOTD:</b> {escape(data['motd'])}\n"
        f"🎮 <b>Версия:</b> {escape(data['version'])}\n"
        f"👤 <b>Игроков:</b> {data['players_online']}/{data['players_max']}"
        f"{players_list}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📡 Статус сервера", callback_data="status")],
        [InlineKeyboardButton("👥 Список игроков", callback_data="players")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Привет! Я бот для мониторинга Minecraft-сервера.\n"
        f"🌐 Сервер: <code>{MC_HOST}:{MC_PORT}</code>",
        reply_markup=markup,
        parse_mode="HTML"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Опрашиваю сервер...")
    data = get_server_status(MC_HOST, MC_PORT, MC_BEDROCK)
    await msg.edit_text(format_status(data), parse_mode="HTML")


async def players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Получаю список игроков...")
    data = get_server_status(MC_HOST, MC_PORT, MC_BEDROCK)

    if not data["online"]:
        await msg.edit_text("🔴 Сервер оффлайн, список недоступен.")
        return

    if not data["players"]:
        text = (
            f"👤 На сервере {data['players_online']} игр."
            if data["players_online"] > 0
            else "😴 Сейчас никого нет на сервере."
        )
    else:
        names = "\n".join(f"  • {escape(n)}" for n in data["players"])
        text = f"👥 <b>Игроки онлайн ({data['players_online']}/{data['players_max']}):</b>\n{names}"

    await msg.edit_text(text, parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = get_server_status(MC_HOST, MC_PORT, MC_BEDROCK)

    if query.data == "status":
        await query.edit_message_text(
            format_status(data),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Обновить", callback_data="status")],
                [InlineKeyboardButton("👥 Игроки", callback_data="players")],
            ])
        )
    elif query.data == "players":
        if not data["online"]:
            text = "🔴 Сервер оффлайн"
        elif not data["players"]:
            text = (
                f"👤 Онлайн: {data['players_online']} чел., список скрыт сервером."
                if data["players_online"] > 0
                else "😴 Никого нет."
            )
        else:
            names = "\n".join(f"  • {escape(n)}" for n in data["players"])
            text = f"👥 <b>Игроки ({data['players_online']}/{data['players_max']}):</b>\n{names}"

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Обновить", callback_data="players")],
                [InlineKeyboardButton("📡 Статус", callback_data="status")],
            ])
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("players", players_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()