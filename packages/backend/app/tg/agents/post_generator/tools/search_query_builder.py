from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict, cast

import structlog
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.core.errors import AppError
from app.core.llm import get_llm, load_prompts
from app.models.base import utc_now

logger = structlog.get_logger()


class ContentProviderPrompts(BaseModel):
    system_prompt: str
    structured_output: str


class AllContentProviderPrompts(BaseModel):
    ru: ContentProviderPrompts


try:
    PROMPTS = load_prompts(
        Path(__file__).parent.parent / "prompts.yaml",
        AllContentProviderPrompts,
        key="search_query_builder",
    )
except:
    logger.error("Failed to load SequeryBuilderPrompts prompts")
    raise


class SearchQueryBulder(BaseTool):
    name: str = "search_query_builder"
    description: str = (
        "Generates a list of search queries based on the input information."
    )

    lang: Literal["en", "ru"] = "ru"
    channel_username: str
    content_description: str
    persona_description: str

    prompts: ContentProviderPrompts

    def __init__(
        self,
        lang: Literal["en", "ru"] = "ru",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(prompts=getattr(PROMPTS, lang), *args, **kwargs)

    def _run(self) -> None:
        raise AppError("This tool is not designed to be run synchronously.")

    async def _arun(
        self,
        user_prompt: str,
    ) -> list[str]:
        context = {
            "current_date": utc_now().strftime("%Y-%m-%d"),
            "channel_username": self.channel_username,
            "content_description": self.content_description,
            "persona_description": self.persona_description,
            "user_prompt": user_prompt,
        }

        class SearchQueries(TypedDict):
            queries: Annotated[list[str], "List of search queries"]

        SearchQueries.__doc__ = self.prompts.structured_output

        prompt_template = ChatPromptTemplate(
            [
                ("system", self.prompts.system_prompt),
                ("user", user_prompt),
            ]
        )
        messages = prompt_template.format_messages(**context)
        logger.debug(f"Generated messages {messages}")

        llm = get_llm().with_structured_output(SearchQueries)
        response = cast(SearchQueries, await llm.ainvoke(messages))

        return response["queries"]
