from uuid import UUID

from telegram import Bot
from telegram.error import BadRequest as TelegramBadRequest
from telegram.error import Forbidden as TelegramForbiddenError

from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.tg.agents.models import TGAgent, TGAgentStatus
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
        # ChatMemberAdministrator(api_kwargs={'can_manage_voice_chats': False}, can_be_edited=False, can_change_info=False, can_delete_messages=False, can_delete_stories=True, can_edit_stories=True, can_invite_users=False, can_manage_chat=True, can_manage_topics=False, can_manage_video_chats=False, can_pin_messages=False, can_post_stories=True, can_promote_members=False, can_restrict_members=False, is_anonymous=False, status=<ChatMemberStatus.ADMINISTRATOR>, user=User(first_name='Бот устарел', id=5365706309, is_bot=True, username='get2gether_antalya_bot'))
        print(member)
    except TelegramForbiddenError:
        # still not a member
        if agent.status == TGAgentStatus.WAITING_BOT_ACCESS:
            return agent
        elif agent.bot_is_connected():
            agent = await agent_svc.waiting_bot_access(agent.id)
            return agent
        return agent
    except TelegramBadRequest as e:
        if "Chat not found" in str(e):
            # still not a member
            if agent.status == TGAgentStatus.WAITING_BOT_ACCESS:
                return agent
            elif agent.bot_is_connected():
                agent = await agent_svc.waiting_bot_access(agent.id)
                return agent
            return agent
        raise
    except Exception as e:
        await agent_svc.save_status_error(agent.id, str(e))
        raise

    return agent
