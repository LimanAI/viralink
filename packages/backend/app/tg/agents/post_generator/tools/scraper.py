import asyncio
from typing import Any

import structlog
import trafilatura
from langchain_core.tools import BaseTool

from app.core.errors import AppError

logger = structlog.get_logger()


class Scraper(BaseTool):
    name: str = "web_page_scraper"
    description: str = (
        "Scrapes a web page and extracts its content if the direct link is provided. "
        "Returns the content in markdown format."
    )

    async def scrape(self, url: str) -> Any:
        def sync_scrape(url: str) -> str:
            response = trafilatura.fetch_url(url)
            data = trafilatura.extract(
                response,
                output_format="markdown",
                favor_precision=True,
                deduplicate=True,
            )
            logger.debug(f"Data scraped: {data}")
            return data or ""

        logger.debug(f"Scraping URL: {url}")
        return await asyncio.get_running_loop().run_in_executor(None, sync_scrape, url)

    def _run(self, url: str) -> Any:
        raise AppError("This tool is not designed to be run synchronously.")

    async def _arun(
        self,
        url: str,
        *_: Any,
        **__: Any,
    ) -> Any:
        return await self.scrape(url)
