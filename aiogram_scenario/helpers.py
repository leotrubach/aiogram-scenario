from typing import Optional, Tuple


def normalize_telegram_ids(*, chat_id: Optional[int] = None, user_id: Optional[int] = None) -> Tuple[int, int]:

    if (chat_id is None) and (user_id is None):
        raise ValueError("'chat_id' or 'user_id' parameter is required but no one is provided!")

    return chat_id or user_id, user_id or chat_id
