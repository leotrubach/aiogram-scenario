import pytest

from aiogramscenario.helpers import (get_chat_id_with_context, get_user_id_with_context,
                                     get_handler_with_context, errors)


class TestGetChatIDWithContext:

    def test_chat_is_set(self, chat):

        chat_id = get_chat_id_with_context()

        assert chat_id == chat.id

    def test_chat_is_not_set(self):

        with pytest.raises(errors.ContextVarNotSet):
            get_chat_id_with_context()


class TestGetUserIDWithContext:

    def test_user_is_set(self, user):

        user_id = get_user_id_with_context()

        assert user_id == user.id

    def test_user_is_not_set(self):

        with pytest.raises(errors.ContextVarNotSet):
            get_user_id_with_context()


class TestGetHandlerWithContext:

    def test_handler_is_set(self, handler):

        handler_ = get_handler_with_context()

        assert handler_ is handler

    def test_handler_is_not_set(self):

        with pytest.raises(errors.ContextVarNotSet):
            get_handler_with_context()
