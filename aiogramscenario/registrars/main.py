from typing import Callable, Iterable, Any

from aiogram import Dispatcher

from aiogramscenario.registrars.scene import SceneRegistrar
from aiogramscenario.scenario.scene import BaseScene


class MainRegistrar:

    def __init__(self, dispatcher: Dispatcher):

        self._dispatcher = dispatcher

    def register_scene_handlers(self, scenes: Iterable[BaseScene], data: Any = None):

        for scene in scenes:
            registrar = SceneRegistrar(self._dispatcher, scene)
            scene.register_handlers(registrar, data)

    def register_message_handler(self, callback: Callable, scenes: Iterable[BaseScene], *custom_filters,
                                 commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for scene in scenes:
            registrar = self._get_scene_registrar(scene)
            registrar.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                               content_types=content_types, run_task=run_task, **kwargs)

    def register_callback_query_handler(self, callback: Callable, scenes: Iterable[BaseScene], *custom_filters,
                                        run_task=None, **kwargs) -> None:

        for scene in scenes:
            registrar = self._get_scene_registrar(scene)
            registrar.register_callback_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_channel_post_handler(self, callback: Callable, scenes: Iterable[BaseScene], *custom_filters,
                                      commands=None, regexp=None, content_types=None, run_task=None, **kwargs) -> None:

        for scene in scenes:
            registrar = self._get_scene_registrar(scene)
            registrar.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                    content_types=content_types, run_task=run_task, **kwargs)

    def register_edited_channel_post_handler(self, callback: Callable, scenes: Iterable[BaseScene], *custom_filters,
                                             commands=None, regexp=None, content_types=None,
                                             run_task=None, **kwargs) -> None:

        for scene in scenes:
            registrar = self._get_scene_registrar(scene)
            registrar.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                           regexp=regexp, content_types=content_types,
                                                           run_task=run_task, **kwargs)

    def register_edited_message_handler(self, callback: Callable, scenes: Iterable[BaseScene], *custom_filters,
                                        commands=None, regexp=None, content_types=None,
                                        run_task=None, **kwargs) -> None:

        for scene in scenes:
            registrar = self._get_scene_registrar(scene)
            registrar.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                      content_types=content_types, run_task=run_task, **kwargs)

    def register_chosen_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_chosen_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_inline_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_inline_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_pre_checkout_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_pre_checkout_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_shipping_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_shipping_query_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_chat_member_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs):

        self._dispatcher.register_chat_member_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_my_chat_member_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs):

        self._dispatcher.register_my_chat_member_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_errors_handler(self, callback: Callable, *custom_filters, exception=None,
                                run_task=None, **kwargs) -> None:

        self._dispatcher.register_errors_handler(callback, *custom_filters, exception=exception,
                                                 run_task=run_task, **kwargs)

    def register_poll_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def register_poll_answer_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_poll_answer_handler(callback, *custom_filters, run_task=run_task, **kwargs)

    def _get_scene_registrar(self, scene: BaseScene) -> SceneRegistrar:

        return SceneRegistrar(self._dispatcher, scene)
