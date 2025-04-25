from collections.abc import Coroutine
from functools import wraps
from typing import Any, Callable, cast, overload

from telegram import Update
from telegram.ext._utils.types import HandlerCallback

from app.tgbot.context import Context

TCallback = HandlerCallback[Update, Context, None]
ExtTCallback = Callable[[None, Update, Context], Coroutine[Any, Any, None]]


@overload
def requires_auth(func: ExtTCallback) -> TCallback: ...


@overload
def requires_auth(*, is_admin: bool = False) -> Callable[[ExtTCallback], TCallback]: ...


def requires_auth(
    *args: Any, **kwargs: Any
) -> TCallback | Callable[[ExtTCallback], TCallback]:
    def _inner(is_admin: bool = False) -> Callable[[ExtTCallback], TCallback]:
        def requires_auth(
            call: ExtTCallback,
        ) -> TCallback:
            @wraps(call)
            def wrapper(
                update: Update, context: Context, *args: Any, **kwargs: Any
            ) -> Coroutine[Any, Any, None]:
                user = None
                return call(user, update, context, *args, **kwargs)

            return wrapper

        return requires_auth

    if len(args) == 1 and callable(args[0]):
        return _inner()(cast(ExtTCallback, args[0]))
    return _inner(*args, **kwargs)
