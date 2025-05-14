import asyncio
from datetime import timedelta
from logging import debug
from pathlib import Path
from typing import Literal
from uuid import UUID

import structlog
from bs4 import BeautifulSoup, Tag
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf import settings
from app.core.errors import AppError
from app.core.llm import (
    ImageLLMModelName,
    LLMModelName,
    get_llm,
    load_prompts,
)

# from app.db import AsyncSessionMaker
from app.db import AsyncSessionMaker
from app.models.base import utc_now
from app.tg.agents.models import (
    PostGenerationMetadata,
    PostUpdateMetadata,
    TGAgent,
    TGAgentJob,
    TGAgentJobStatus,
    TGAgentJobType,
    TGAgentStatus,
)
from app.tg.agents.post_generator.tools.content_provider import ContentProvider
from app.tg.agents.post_generator.tools.image_generator import (
    ImageGenerator,
    ImageGeneratorQueryBuilderPrompts,
)
from app.tg.agents.post_generator.tools.publisher import Publisher
from app.tg.agents.post_generator.tools.scraper import Scraper
from app.tg.agents.services import TGAgentJobService, TGAgentService
from app.tg.credits.services import spend_credits

logger = structlog.get_logger()


class MainPrompts(BaseModel):
    system_prompt: str


class UpdatePostPrompts(BaseModel):
    system_prompt: str
    user_prompt: str


class DefineActionPrompts(BaseModel):
    system_prompt: str
    user_prompt: str


class GeneratePrompts(BaseModel):
    main: MainPrompts
    define_action: DefineActionPrompts
    update_post: UpdatePostPrompts
    image_generator_query_builder: ImageGeneratorQueryBuilderPrompts


class PostGeneratorPrompts(BaseModel):
    ru: GeneratePrompts


try:
    PROMPTS = load_prompts(
        Path(__file__).parent / "prompts.yaml",
        PostGeneratorPrompts,
        key="post_generator",
    )
except:
    logger.error("Failed to load PostGenerator prompts")
    raise


class PostGenerator:
    def __init__(
        self,
        db_session_maker: AsyncSessionMaker,
        db_session: AsyncSession,
        lang: Literal["en", "ru"] = "ru",
        model: LLMModelName = "o4-mini",
        image_model: ImageLLMModelName = "recraft-ai/recraft-v3",
    ) -> None:
        self.db_session_maker = db_session_maker
        self.db_session = db_session

        self.model: LLMModelName = model
        self.image_model: ImageLLMModelName = image_model

        self.lang = lang
        self.prompts = getattr(PROMPTS, lang)

    async def generate(self, job: TGAgentJob) -> str:
        job = self._validate_job(job)

        agent_svc = TGAgentService(self.db_session)
        agent_job_svc = TGAgentJobService(self.db_session)

        if not job.agent_id:
            raise AppError("Job is detached from agent", job_id=job.id)
        agent = await agent_svc.get(job.agent_id, with_bot=True)
        agent = self._validate_agent(agent, job)

        if not agent.tg_user_id:
            raise AppError("Agent is orphaned", agent_id=agent.id)

        async with spend_credits(self.db_session, agent.tg_user_id, 1):
            job = await agent_job_svc.in_progress(job.id)

        message_post = await self._generate_post(job, agent)
        return keep_only_allowed_tags(message_post)

    async def update(self, job: TGAgentJob) -> dict[str, str | None]:
        job = self._validate_job(job)

        agent_svc = TGAgentService(self.db_session)
        agent_job_svc = TGAgentJobService(self.db_session)

        if not job.agent_id:
            raise AppError("Job is detached from agent", job_id=job.id)
        agent = await agent_svc.get(job.agent_id, with_bot=True)
        agent = self._validate_agent(agent, job)

        job = await agent_job_svc.in_progress(job.id)

        output = await self._update_post(job, agent)
        message_post = output.get("message")
        if message_post:
            output["message"] = keep_only_allowed_tags(message_post)
        return output

    async def _generate_post(self, job: TGAgentJob, agent: TGAgent) -> str:
        metadata = PostGenerationMetadata.model_validate(job.metadata_)
        tools = {
            "content_provider": ContentProvider(**agent.get_summary()),
            "web_page_scraper": Scraper(),
        }
        llm = get_llm(self.model).bind_tools(list(tools.values()))

        prompt_template = ChatPromptTemplate(
            [
                ("system", self.prompts.main.system_prompt),
                ("system", self.prompts.define_action.system_prompt),
                ("user", metadata.user_prompt),
            ]
        )

        messages = prompt_template.format_messages(**agent.get_summary())
        result = await llm.ainvoke(messages)

        # how to build messages?
        if tool_calls := getattr(result, "tool_calls", []):
            messages.append(result)
            for tool_call in tool_calls:
                tool = tools[tool_call["name"]]
                tool_call["args"]["user_prompt"] = metadata.user_prompt
                output = await tool.ainvoke(tool_call)
                messages.append(output)
            result = await llm.ainvoke(messages)

        if not isinstance(result.content, str):
            raise AppError("result.content is not a string", job_id=job.id)
        return result.content

    async def _update_post(
        self, job: TGAgentJob, agent: TGAgent
    ) -> dict[str, str | None]:
        tg_user_id = agent.tg_user_id
        if not tg_user_id:
            raise AppError("Agent is orphaned", agent_id=agent.id)
        metadata = PostUpdateMetadata.model_validate(job.metadata_)
        tools = {
            "publish": Publisher(
                chat_id=metadata.chat_id,
            ),
            "image_generator": ImageGenerator(
                model=self.model,
                image_model=self.image_model,
                prompts=self.prompts.image_generator_query_builder,
            ),
        }
        llm = get_llm(self.model).bind_tools(list(tools.values()))

        prompt_template = ChatPromptTemplate(
            [
                ("system", self.prompts.main.system_prompt),
                ("system", self.prompts.update_post.system_prompt),
                ("user", self.prompts.update_post.user_prompt),
                ("user", metadata.user_prompt),
            ]
        )

        messages = prompt_template.format_messages(
            **{
                **agent.get_summary(),
                "original_message": metadata.original_message,
            }
        )
        result = await llm.ainvoke(messages)
        debug(result)

        image = None
        message = result.content
        # how to build messages?
        if tool_calls := getattr(result, "tool_calls", []):
            for tool_call in tool_calls:
                tool = tools[tool_call["name"]]
                if tool_call["name"] == "publish":
                    tool_call["args"]["post"] = metadata.original_message
                    tool_call["args"]["job_id"] = job.id
                    await tool.ainvoke(tool_call)
                    return {}
                elif tool_call["name"] == "image_generator":
                    # TODO: refactor
                    if len(metadata.original_message) > 1000:
                        raise AppError(
                            "Message is too long for generating image",
                            job_id=job.id,
                            code=2200,
                        )
                    tool_call["args"]["post"] = metadata.original_message
                    try:
                        async with spend_credits(self.db_session, tg_user_id, 2):
                            result = await tool.ainvoke(tool_call)
                            image = (
                                result.content
                                if isinstance(result.content, str)
                                else None
                            )
                            if not image:
                                raise AppError(
                                    "Could not generate image", job_id=job.id
                                )
                    except Exception as e:
                        logger.exception(e)
                    message = metadata.original_message

        if not isinstance(message, str):
            raise AppError("result.content is not a string", job_id=job.id)
        return {"image": image, "message": message}

    def _validate_agent(self, agent: TGAgent | None, job: TGAgentJob) -> TGAgent:
        if not agent:
            raise AppError("Agent not found", job_id=job.id)

        if agent.status != TGAgentStatus.ACTIVE:
            raise AppError("Agent is not active", agent_id=agent.id, job_id=job.id)

        content_description = agent.channel_profile.content_description
        if not content_description:
            raise AppError(
                "Channel profile content description is missing", agent_id=agent.id
            )

        persona_description = agent.channel_profile.persona_description
        if not persona_description:
            raise AppError(
                "Channel profile persona description is missing", agent_id=agent.id
            )
        return agent

    def _validate_job(self, job: TGAgentJob) -> TGAgentJob:
        if (
            job.type_ != TGAgentJobType.POST_GENERATION
            and job.type_ != TGAgentJobType.POST_UPDATE
        ):
            raise AppError(
                f"Job is not a root job with POST_GENERATION or POST_UPDATE type, actual {job.type_}",
                job_id=job.id,
            )

        check_if_job_staled(job)
        if job.status != TGAgentJobStatus.INITIAL:
            raise AppError(
                f"Job is not in INITIAL status, actual {job.status}", job_id=job.id
            )
        return job


# TODO: refactor, move to utils or whatever
def check_if_job_staled(job: TGAgentJob, minutes: int = 30) -> None:
    if (
        job.status == TGAgentJobStatus.IN_PROGRESS
        and job.status_changed_at
        and job.status_changed_at < (utc_now() - timedelta(minutes=minutes))
    ):
        raise AppError("Job is staled", job_id=job.id)


def keep_only_allowed_tags(html: str) -> str:
    allowed_tags = {"a", "b", "i", "pre", "u", "s", "code"}
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        if isinstance(tag, Tag) and tag.name not in allowed_tags:
            tag.unwrap()

    return str(soup)
