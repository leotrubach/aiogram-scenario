import logging

from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import current_handler
from aiogram.types import User, Chat

from .scenario import Scenario


logger = logging.getLogger(__name__)


class ScenarioMiddleware(BaseMiddleware):
    """ Middleware for switching target_state. """

    def __init__(self, scenario: Scenario, dispatcher: Dispatcher):

        super().__init__()
        self._scenario = scenario
        self._dispatcher = dispatcher

    @staticmethod
    def save_pointing_handler(data: dict) -> None:
        """ Saves the object of the current context handler. """

        pointing_handler = current_handler.get()
        data["pointing_handler"] = pointing_handler
        logger.debug(f"Current pointing handler saved: {pointing_handler}")

    async def execute_transition(self, update, results: list, data: dict) -> None:
        """ Executes request for transition to the next target_state. """

        logger.debug("Update received, transition process started...")
        pointing_handler = data.get("pointing_handler")
        logger.debug(f"Got a pointing handler: {pointing_handler}")
        if pointing_handler is not None:
            for result in results:
                if isinstance(result, Exception):
                    break
            else:
                target_state = self._scenario.states_map.get_target_state(pointing_handler)
                logger.debug(f"Got the target state: {target_state}")
                if target_state is not None:
                    user = User.get_current()
                    chat = Chat.get_current()
                    handler_args = (update,)

                    await self._scenario.execute_transition(target_state, user.id,
                                                            chat.id if chat is not None else None,
                                                            *handler_args, **data)

    async def on_process_message(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_edited_message(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_channel_post(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_edited_channel_post(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_inline_query(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_chosen_inline_result(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_callback_query(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_shipping_query(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_process_pre_checkout_query(self, _, data: dict):

        self.save_pointing_handler(data)

    async def on_post_process_message(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_edited_message(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_channel_post(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_edited_channel_post(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_inline_query(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_chosen_inline_result(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_callback_query(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_shipping_query(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)

    async def on_post_process_pre_checkout_query(self, update, results: list, data: dict):

        await self.execute_transition(update, results, data)
