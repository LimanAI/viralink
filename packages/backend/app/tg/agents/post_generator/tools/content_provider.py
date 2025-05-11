from typing import Any, Literal, cast

import structlog
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool

from app.core.errors import AppError
from app.tg.agents.post_generator.tools.scraper import Scraper
from app.tg.agents.post_generator.tools.search_query_builder import SearchQueryBulder

logger = structlog.get_logger()


class ContentProvider(BaseTool):
    name: str = "content_provider"
    description: str = (
        "Provides additional content for the channel based on the input information."
    )

    channel_username: str
    content_description: str
    persona_description: str

    def _run(self) -> None:
        raise AppError("This tool is not designed to be run synchronously.")

    async def _arun(
        self,
        user_prompt: str,
        type_: str = "search_in_web",
    ) -> dict[str, Any]:
        queries = await SearchQueryBulder(
            channel_username=self.channel_username,
            content_description=self.content_description,
            persona_description=self.persona_description,
        ).ainvoke(user_prompt)

        logger.debug(f"Generated search queries: {queries}")

        results = await DuckDuckGoSearchResults(
            num_results=1, output_format="list"
        ).ainvoke(queries[0])

        logger.debug(f"Search result: {results}")

        result = results[0]
        result["data"] = await Scraper().ainvoke(result["link"])
        return cast(dict[str, Any], result)
