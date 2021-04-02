from typing import Optional, Tuple
from inspect import FullArgSpec


def normalize_telegram_ids(*, chat_id: Optional[int] = None, user_id: Optional[int] = None) -> Tuple[int, int]:

    if (chat_id is None) and (user_id is None):
        raise ValueError("'chat_id' or 'user_id' parameter is required but no one is provided!")

    return chat_id or user_id, user_id or chat_id


def get_kwargs_from_spec(spec: FullArgSpec, kwargs: dict) -> dict:

    return kwargs if spec.varkw else {k: v for k, v in kwargs.items()
                                      if k in set(spec.args + spec.kwonlyargs)}
