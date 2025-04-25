from typing import Any

from telegram.ext import CallbackContext, ExtBot


class Context(
    CallbackContext[ExtBot[None], dict[Any, Any], dict[Any, Any], dict[Any, Any]]
): ...
