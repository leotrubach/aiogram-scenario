import inspect
from typing import Callable


def get_existing_kwargs(callback: Callable, check_varkw: bool = False, **kwargs: dict) -> dict:

    spec = inspect.getfullargspec(callback)
    if check_varkw and (spec.varkw is not None):
        return kwargs

    return {k: v for k, v in kwargs.items() if k in spec.args}
