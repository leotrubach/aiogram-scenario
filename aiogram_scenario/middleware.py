from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import User, Chat

from .fsm import FSM, FSMPointer


fsm_arg_name = "fsm"  # can be changed to another


class FSMMiddleware(BaseMiddleware):
    """ Middleware for switching target_state. """

    def __init__(self, fsm: FSM):

        super().__init__()
        self._fsm = fsm

    async def on_process(self, _, data: dict):

        self._setup_fsm_pointer(data)

    async def on_process_error(self, _, exception, data):

        self._setup_fsm_pointer(data)

    on_process_message = on_process

    on_process_edited_message = on_process

    on_process_channel_post = on_process

    on_process_edited_channel_post = on_process

    on_process_inline_query = on_process

    on_process_chosen_inline_result = on_process

    on_process_callback_query = on_process

    on_process_shipping_query = on_process

    on_process_pre_checkout_query = on_process

    def _setup_fsm_pointer(self, data: dict):

        user = User.get_current()
        chat = Chat.get_current()

        chat_id = chat.id if chat is not None else None
        user_id = user.id if user is not None else None

        data[fsm_arg_name] = FSMPointer(fsm=self._fsm, user_id=user_id, chat_id=chat_id)
