from itertools import groupby
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import (
    GetParticipantRequest,
    JoinChannelRequest,
)
from telethon.tl.types import InputChannel, InputPeerChannel

from app.services import BaseService
from app.tg.accounts.models import TGAccountModel, TGAccountStatus
from app.tg.accounts.repositories import TGAccountRepository
from app.tg.accounts.services import TGAccountService

from .models import TGAgent, TGChannelConnection, TGChannelConnectionStatus
from .repositories import (
    TGAgentRepository,
    TGChannelConnectionRepository,
    TGChannelRepository,
)

logger = structlog.get_logger()


class TGAgentService(BaseService):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        # repositories
        self.tg_agent_repo = TGAgentRepository(db_session)

        # services
        self.tg_account_svc = TGAccountService(db_session)
        self.tg_channel_connection_svc = TGChannelConnectionService(db_session)

    async def create_agent(
        self,
        channel_handle: str,
        tg_user_id: int | None = None,
        user_id: UUID | None = None,
    ) -> TGAgent:
        if not tg_user_id and not user_id:
            raise ValueError("Either tg_user_id or user_id must be provided")
        if tg_user_id is not None and user_id is not None:
            raise ValueError("Only one of tg_user_id or user_id must be provided")

        tg_account = await self.tg_account_svc.get_available()

        channel_handle = channel_handle.lstrip("@")
        # Getting channel entity (id and access_hash)
        async with self.tg_account_svc.get_tgclient(tg_account) as tgclient:
            logger.info(f"Trying to get channel entity: {channel_handle}")
            channel = await tgclient.get_input_entity(channel_handle)
            logger.info(f"Channel entity {channel}")
            if not isinstance(channel, InputPeerChannel):
                raise ValueError("Invalid channel handle")

        tg_agent = await self.tg_agent_repo.get_for_channel(
            channel.channel_id, tg_user_id=tg_user_id, user_id=user_id
        )
        if tg_agent:
            logger.info(f"Found existing agent for channel {tg_agent}")
            return tg_agent

        # Creating channel connection
        tg_channel_connection = (
            await self.tg_channel_connection_svc.get_or_create_connection(
                channel.channel_id,
                channel_link=channel_handle,
                recover=True,
                check=True,
            )
        )
        tg_agent = await self.tg_agent_repo.create(
            tg_channel_connection.tg_channel_id,
            tg_channel_connection.tg_account_id,
            tg_user_id=tg_user_id,
            user_id=user_id,
        )
        logger.info(f"Created an agent for channel {tg_agent}")
        return tg_agent


class TGChannelConnectionService(BaseService):
    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(db_session)
        # repositories
        self.tg_channel_connection_repo = TGChannelConnectionRepository(db_session)
        self.tg_account_repo = TGAccountRepository(db_session)
        self.tg_channel_repo = TGChannelRepository(db_session)

        # services
        self.tg_account_svc = TGAccountService(db_session)

    async def get_or_create_connection(
        self,
        tg_channel_id: int,
        channel_link: str,
        *,
        recover: bool = False,
        check: bool = True,
    ) -> TGChannelConnection:
        """
        Get or create a channel connection for the given channel ID.
        Try to recover failed connection if recover is True.
        Check that the connection is active if check is True
        """
        connections = await self.tg_channel_connection_repo.list(tg_channel_id)
        if not connections:
            # creating
            logger.debug("No connections found, creating a new one")
            for tg_account in await self.tg_account_repo.list():
                try:
                    connection = await self._create_connection_with_account(
                        tg_account.id, tg_channel_id, channel_link
                    )
                except Exception as e:
                    logger.exception(e)
                else:
                    logger.info(f"Created a new connection {connection}")
                    return connection
            raise ValueError("No available accounts to create a connection")

        connections = sorted(connections, key=lambda x: x.status)
        grouped_connections = {
            status: list(connections)
            for status, connections in groupby(connections, key=lambda x: x.status)
        }
        checked_tg_accounts = set()

        # first check any connected
        alive_connections = grouped_connections.get(
            TGChannelConnectionStatus.CONNECTED, []
        )
        for connection in alive_connections:
            if not check:
                logger.info(f"Connection {connection} is alive")
                return connection

            if self.check_connection(
                connection, recover=recover, channel_link=channel_link
            ):
                logger.info(f"Connection {connection} is alive, checked")
                return connection
            checked_tg_accounts.add(connection.tg_account_id)

        if recover:
            # try to reconnect disconnected connections
            disconnected_connections = grouped_connections.get(
                TGChannelConnectionStatus.DISCONNECTED, []
            )
            for connection in disconnected_connections:
                if self.check_connection(
                    connection, recover=True, channel_link=channel_link
                ):
                    logger.info(f"Connection {connection} is alive, recovered")
                    return connection

        # if no connections create a new one
        new_accounts = await self.tg_account_repo.list(
            exclude_ids=list(checked_tg_accounts)
        )
        if not new_accounts:
            raise ValueError("No available accounts to create a connection")

        # create a new connection
        for new_account in new_accounts:
            try:
                connection = await self._create_connection_with_account(
                    new_account.id, tg_channel_id, channel_link=channel_link
                )
            except Exception as e:
                logger.exception(e)
            else:
                logger.info(f"Created a new connection {connection}")
                return connection
        raise ValueError("No available accounts to create a connection")

    async def check_connection(
        self,
        connection: TGChannelConnection,
        *,
        recover: bool = False,
        channel_link: str | None = None,
    ) -> bool:
        """
        Check the connection status of the given channel connection.
        If the connection is not alive, update its status to "disconnected".
        If recover is True, try to reconnect.
        """
        tg_account = await self.tg_account_repo.get_account(connection.tg_account_id)
        if not tg_account:
            raise ValueError("Account not found [non-consistency]")

        try:
            async with self.tg_account_svc.get_tgclient(tg_account) as tgclient:
                input_channel = InputChannel(
                    channel_id=connection.tg_channel_id,
                    access_hash=connection.access_hash,
                )

                me = await tgclient.get_input_entity("me")
                await tgclient(GetParticipantRequest(input_channel, me))

                if connection.status != TGChannelConnectionStatus.CONNECTED:
                    await self.tg_channel_connection_repo.update_status(
                        connection.tg_channel_id,
                        TGChannelConnectionStatus.CONNECTED,
                    )
        except UserNotParticipantError:
            if not recover:
                raise
            if not channel_link:
                raise ValueError("Channel link is required for recovery") from None

            # Getting access_hash
            async with self.tg_account_svc.get_tgclient(tg_account) as tgclient:
                channel = await tgclient.get_input_entity(channel_link)
                if not isinstance(channel, InputPeerChannel):
                    raise ValueError("Invalid channel link") from None

            await self._join_channel(
                tg_account, connection.tg_channel_id, channel.access_hash
            )
            await self.tg_channel_connection_repo.update_status(
                connection.tg_channel_id,
                TGChannelConnectionStatus.CONNECTED,
                access_hash=channel.access_hash,
            )
        except Exception as e:
            await self.tg_channel_connection_repo.update_status(
                connection.tg_channel_id,
                TGChannelConnectionStatus.DISCONNECTED,
                error=str(e),
            )
            return False
        return True

    async def _create_connection_with_account(
        self, tg_account_id: UUID, tg_channel_id: int, channel_link: str
    ) -> TGChannelConnection:
        """
        Create a new channel connection (and join to the channel) with the given tg_account.
        """
        tg_account = await self.tg_account_repo.get_account(tg_account_id)
        if not tg_account:
            raise ValueError("Account not found")

        if tg_account.status != TGAccountStatus.ACTIVE:
            raise ValueError("Account is not active")

        tg_channel = await self.tg_channel_repo.get_or_create(tg_channel_id)

        # getting access_hash
        async with self.tg_account_svc.get_tgclient(tg_account) as tgclient:
            channel = await tgclient.get_input_entity(channel_link)
            if not isinstance(channel, InputPeerChannel):
                raise ValueError("Invalid channel handle")
            access_hash = channel.access_hash

        # joining
        await self._join_channel(tg_account, tg_channel.tg_channel_id, access_hash)
        connection = await self.tg_channel_connection_repo.create(
            tg_account.id, tg_channel.tg_channel_id, access_hash
        )
        return connection

    async def _join_channel(
        self, tg_account: TGAccountModel, tg_channel_id: int, access_hash: int
    ) -> None:
        """
        Join a channel using the provided tg_account and tg_channel_id.
        """
        async with self.tg_account_svc.get_tgclient(tg_account) as tgclient:
            logger.info(f"Joining channel {tg_channel_id} with account {tg_account.id}")

            input_channel = InputChannel(
                channel_id=tg_channel_id,
                access_hash=access_hash,
            )
            await tgclient(JoinChannelRequest(input_channel))
