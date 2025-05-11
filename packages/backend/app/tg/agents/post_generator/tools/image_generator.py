from logging import debug

from langchain_community.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.errors import AppError
from app.core.llm import ImageLLMModelName, LLMModelName, get_image_llm, get_llm


class ImageGeneratorQueryBuilderPrompts(BaseModel):
    system_prompt: str


class ImageGenerator(BaseTool):
    """
    Generates image for the post
    """

    name: str = "image_generator"
    description: str = "Generates image for the post."

    prompts: ImageGeneratorQueryBuilderPrompts
    model: LLMModelName
    image_model: ImageLLMModelName

    def _run(self) -> None:
        raise AppError("This tool is not designed to be run synchronously.")

    async def _arun(self, post: str) -> str:
        prompt_template = ChatPromptTemplate(
            [
                ("system", self.prompts.system_prompt),
                ("user", post),
            ]
        )
        messages = prompt_template.format_messages()
        debug(messages)

        llm = get_llm(self.model)
        response = await llm.ainvoke(messages)

        if not isinstance(response.content, str):
            raise AppError("result.content is not a string")

        debug(response)
        image_llm = get_image_llm(self.image_model)

        image_url = await image_llm.ainvoke(response.content)
        if not isinstance(image_url, str):
            raise AppError("image_url is not a string")
        return image_url
