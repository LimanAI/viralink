from uuid import UUID

from telegram import Bot
from telegram.constants import ChatType
from telegram.error import BadRequest as TelegramBadRequest
from telegram.error import Forbidden as TelegramForbiddenError

from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.tg.agents.models import BotPermissions, TGAgent, TGAgentStatus
from app.tg.agents.services import TGAgentService


async def check_agent_bot_permissions(
    tg_user_id: int, agent_id: UUID, agent_svc: TGAgentService
) -> TGAgent:
    """
    Check if the bot has permissions to send messages to the channel.
    If not, update the agent status to WAITING_BOT_ACCESS.

    TODO: handle the case when the bot was deleted from Telegram
    """

    agent = await agent_svc.get(agent_id, with_bot=True)
    if not agent:
        raise NotFoundError(f"Agent {agent_id} not found")

    if agent.tg_user_id != tg_user_id:
        raise ForbiddenError(f"Agent {agent_id} does not belong to user {tg_user_id}")

    user_bot = agent.user_bot
    if not user_bot:
        await agent_svc.waiting_bot_attach(agent.id)
        return agent

    bot = Bot(user_bot.api_token)
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{agent.channel_username}", user_id=user_bot.tg_id
        )
        chat = await bot.get_chat(f"@{agent.channel_username}")

        if chat.type != ChatType.CHANNEL:
            raise AppError("Chat is not a channel")

        async with agent_svc.tx():
            await agent_svc.update_channel_metadata(
                agent.id,
                channel_metadata=chat,
            )

            agent = await agent_svc.update_bot_permissions(
                agent.id,
                user_bot.id,
                bot_permissions=BotPermissions(**member.to_dict()),
            )

        if (
            not agent.channel_profile.persona_description
            or not agent.channel_profile.content_description
        ):
            # if the agent doesn't have fully tuned channel_profile
            agent = await agent_svc.waiting_channel_profile(agent.id)
            return agent

        agent = await agent_svc.activate(agent.id)
    except TelegramForbiddenError:
        # still not a member
        if agent.status == TGAgentStatus.WAITING_BOT_ACCESS:
            return agent
        elif agent.bot_is_connected():
            agent = await agent_svc.waiting_bot_access(agent.id)
            return agent
        return agent
    except TelegramBadRequest as e:
        if "Chat not found" in str(e) or "Member list is inaccessible" in str(e):
            # still not a member
            if agent.status == TGAgentStatus.WAITING_BOT_ACCESS:
                return agent
            elif agent.bot_is_connected():
                agent = await agent_svc.waiting_bot_access(agent.id)
                return agent
            return agent
        raise
    except Exception as e:
        await agent_svc.save_status_error(agent_id, str(e))
        raise

    return agent
