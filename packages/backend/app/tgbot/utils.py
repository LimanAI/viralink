from telegram import Update

from app.tgbot.schemas import UserTGData


def extract_user_data(update: Update) -> UserTGData | None:
    try:
        user = next(
            getattr(update, attr)
            for attr in [
                "message",
                "inline_query",
                "chosen_inline_result",
                "callback_query",
                "poll",
                "poll_answer",
            ]
            if hasattr(update, attr)
        ).from_user
    except StopIteration:
        return None

    return UserTGData.model_validate_json(user.to_json())
