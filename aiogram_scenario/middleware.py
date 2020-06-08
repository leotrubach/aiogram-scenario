from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import current_handler
from aiogram.types.update import (Message, InlineQuery, ChosenInlineResult, CallbackQuery,
                                  ShippingQuery, PreCheckoutQuery)

from .scenario import Scenario


class ScenarioMiddleware(BaseMiddleware):
    """ Middleware for switching state. """

    def __init__(self, scenario: Scenario, dispatcher: Dispatcher):

        super().__init__()
        self._scenario = scenario
        self._dispatcher = dispatcher

    @staticmethod
    def save_pointing_handler(data: dict) -> None:
        """ Saves the object of the current context handler. """

        pointing_handler = current_handler.get()
        data["pointing_handler"] = pointing_handler

    async def execute_transition(self, update, data: dict) -> None:
        """ Executes request for transition to the next state. """

        pointing_handler = data.get("pointing_handler")
        if (pointing_handler is not None) and (self._scenario.check_target_state_existence(pointing_handler)):
            fsm_context = self._dispatcher.current_state()
            await self._scenario.execute_transition(pointing_handler, fsm_context, update, context_data=data)

    async def on_process_message(self, update: Message, data: dict):

        self.save_pointing_handler(data)

    async def on_process_edited_message(self, update: Message, data: dict):

        self.save_pointing_handler(data)

    async def on_process_channel_post(self, update: Message, data: dict):

        self.save_pointing_handler(data)

    async def on_process_edited_channel_post(self, update: Message, data: dict):

        self.save_pointing_handler(data)

    async def on_process_inline_query(self, update: InlineQuery, data: dict):

        self.save_pointing_handler(data)

    async def on_process_chosen_inline_result(self, update: ChosenInlineResult, data: dict):

        self.save_pointing_handler(data)

    async def on_process_callback_query(self, update: CallbackQuery, data: dict):

        self.save_pointing_handler(data)

    async def on_process_shipping_query(self, update: ShippingQuery, data: dict):

        self.save_pointing_handler(data)

    async def on_process_pre_checkout_query(self, update: PreCheckoutQuery, data: dict):

        self.save_pointing_handler(data)

    async def on_post_process_message(self, update: Message, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_edited_message(self, update: Message, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_channel_post(self, update: Message, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_edited_channel_post(self, update: Message, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_inline_query(self, update: InlineQuery, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_chosen_inline_result(self, update: ChosenInlineResult, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_callback_query(self, update: CallbackQuery, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_shipping_query(self, update: ShippingQuery, results: list, data: dict):

        await self.execute_transition(update, data)

    async def on_post_process_pre_checkout_query(self, update: PreCheckoutQuery, results: list, data: dict):

        await self.execute_transition(update, data)
