import asyncio
from typing import Any, cast

import structlog
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool
from langchain_google_community import GoogleSearchAPIWrapper

from app.conf import settings
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

    def __init__(self, *arg: Any, **kwargs: Any) -> None:
        super().__init__(*arg, **kwargs)

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

        results = await self._search_google(queries[0])

        logger.debug(f"Search result: {results}")

        result = results[0]
        result["data"] = await Scraper().ainvoke(result["link"])
        return result

    async def _search_duckduckgo(
        self,
        query: str,
        num_results: int = 1,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        search = DuckDuckGoSearchResults(
            num_results=num_results, output_format="list", **kwargs
        )
        return cast(list[dict[str, Any]], await search.ainvoke(query))

    async def _search_google(
        self,
        query: str,
        num_results: int = 1,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        def sync_search(query: str) -> list[dict[str, Any]]:
            api_wrapper = GoogleSearchAPIWrapper(
                google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
                google_cse_id=settings.GOOGLE_CSE_ID.get_secret_value(),
                k=num_results,
            )
            return cast(
                list[dict[str, Any]], api_wrapper.results(query, num_results, **kwargs)
            )

        result = await asyncio.get_running_loop().run_in_executor(
            None, sync_search, query
        )
        return result
