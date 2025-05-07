from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters

from app.tg.agents.services import TGAgentService
from app.tgbot.context import Context
from app.tgbot.decorators import db_session, requires_auth


@db_session
async def init_add_channel(update: Update, context: Context) -> int:
    chat = update.effective_chat
    if not chat:
        raise Exception("chat is None")

    await chat.send_message(
        text="Please enter the channel name (e.g., @example_channel):"
    )
    return 0


@db_session
@requires_auth
async def add_channel(update: Update, context: Context) -> int:
    tg_user = context.tg_user
    if not tg_user:
        raise Exception("tg_user is None")
    db_session = context.db_session
    if not db_session:
        raise Exception("db_session is None")

    tg_agent_svc = TGAgentService(db_session)
    chat = update.effective_chat
    if not chat:
        raise Exception("chat is None")

    message = update.message
    if not message:
        await chat.send_message(text="Invalid message. Please try again.")
        return ConversationHandler.END

    channel_handle = message.text
    if not channel_handle:
        await message.reply_text(text="Invalid channel name. Please try again.")
        return ConversationHandler.END

    # await tg_agent_svc.create_agent(channel_handle, tg_user_id=tg_user.tg_id)
    print(tg_agent_svc)
    return ConversationHandler.END


handlers = [
    ConversationHandler(
        entry_points=[CommandHandler("add_channel", init_add_channel)],
        states={
            0: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_channel),
            ]
        },
        fallbacks=[],
    ),
]
