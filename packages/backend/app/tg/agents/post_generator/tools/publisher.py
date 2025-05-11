from uuid import UUID

from langchain_core.tools import BaseTool
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from app.conf import settings
from app.core.errors import AppError


class Publisher(BaseTool):
    """
    Publishes the post to the channel.
    """

    name: str = "publish"
    description: str = "Publishes the post to the channel."

    chat_id: int

    def _run(self) -> None:
        raise AppError("This tool is not designed to be run synchronously.")

    async def _arun(self, job_id: UUID, post: str, image: str | None = None) -> None:
        await Bot(settings.TGBOT_TOKEN.get_secret_value()).send_message(
            chat_id=self.chat_id,
            text=post,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Publish", callback_data=f"/publish-post/{job_id}"
                        ),
                        InlineKeyboardButton(
                            "Cancel", callback_data=f"/cancel-publish-post/{job_id}"
                        ),
                    ]
                ]
            ),
            parse_mode="HTML",
        )
