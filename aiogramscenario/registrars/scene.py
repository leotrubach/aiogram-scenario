from __future__ import annotations
from typing import Callable, TYPE_CHECKING

from aiogram import Dispatcher

if TYPE_CHECKING:
    from aiogramscenario.scenario.scene import BaseScene


class SceneRegistrar:

    def __init__(self, dispatcher: Dispatcher, scene: BaseScene):

        self._dispatcher = dispatcher
        self._scene = scene

    def register_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                 content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                  content_types=content_types, scene=self._scene,
                                                  run_task=run_task, **kwargs)

    def register_callback_query_handler(self, callback: Callable, *custom_filters, run_task=None, **kwargs) -> None:

        self._dispatcher.register_callback_query_handler(callback, *custom_filters, scene=self._scene,
                                                         run_task=run_task, **kwargs)

    def register_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                      content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_channel_post_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                       content_types=content_types, scene=self._scene,
                                                       run_task=run_task, **kwargs)

    def register_edited_channel_post_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                             content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_channel_post_handler(callback, *custom_filters, commands=commands,
                                                              regexp=regexp, content_types=content_types,
                                                              scene=self._scene, run_task=run_task, **kwargs)

    def register_edited_message_handler(self, callback: Callable, *custom_filters, commands=None, regexp=None,
                                        content_types=None, run_task=None, **kwargs) -> None:

        self._dispatcher.register_edited_message_handler(callback, *custom_filters, commands=commands, regexp=regexp,
                                                         content_types=content_types, scene=self._scene,
                                                         run_task=run_task, **kwargs)
