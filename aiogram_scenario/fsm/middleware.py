from aiogram.dispatcher.middlewares import BaseMiddleware

from .fsm import FiniteStateMachine
from .trigger import FSMTrigger


class FSMMiddleware(BaseMiddleware):

    def __init__(self, fsm: FiniteStateMachine, trigger_arg: str = "fsm"):

        super().__init__()
        self._fsm = fsm
        self._trigger = FSMTrigger(self._fsm)
        self._trigger_arg = trigger_arg

    async def on_process(self, _, data: dict):

        self._setup_trigger(data)

    async def on_process_error(self, _, exception: Exception, data: dict):  # noqa

        self._setup_trigger(data)

    on_process_message = on_process

    on_process_edited_message = on_process

    on_process_channel_post = on_process

    on_process_edited_channel_post = on_process

    on_process_inline_query = on_process

    on_process_chosen_inline_result = on_process

    on_process_callback_query = on_process

    on_process_shipping_query = on_process

    on_process_pre_checkout_query = on_process

    def _setup_trigger(self, data: dict) -> None:

        data[self._trigger_arg] = self._trigger
