import inspect
from typing import Callable, Optional, Tuple


def get_existing_kwargs(callback: Callable, kwargs: dict, check_varkw: bool = False) -> dict:

    spec = inspect.getfullargspec(callback)
    if check_varkw and (spec.varkw is not None):
        return kwargs

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}


def resolve_address(*, chat_id: Optional[int] = None, user_id: Optional[int] = None) -> Tuple[int, int]:

    if (chat_id is None) and (user_id is None):
        raise ValueError("'chat_id' or 'user_id' parameter is required but no one is provided!")

    return chat_id or user_id, user_id or chat_id
