from aiogram.dispatcher.middlewares import BaseMiddleware

from .fsm import FSM
from .trigger import FSMTrigger


class FSMMiddleware(BaseMiddleware):

    def __init__(self, fsm: FSM, *, trigger_kwarg: str = "fsm"):

        super().__init__()
        self._fsm = fsm
        self._trigger = FSMTrigger(self._fsm)
        self._trigger_kwarg = trigger_kwarg

    async def on_process(self, _, data: dict) -> None:

        self._setup_trigger(data)

    async def on_process_error(self, _, __, data: dict) -> None:

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

        data[self._trigger_kwarg] = self._trigger
