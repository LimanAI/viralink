from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler

from app.tgbot.context import Context
from app.tgbot.utils import extract_user_data


async def start(update: Update, _: Context) -> None:
    user_data = extract_user_data(update)
    if user_data is None:
        raise ValueError("User data is None")

    chat = update.effective_chat
    if not chat:
        return

    await chat.send_message(
        text="Welcome to *ViraLink*\\!\n\n",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


handlers = [
    CommandHandler("start", start),
]
