from dataclasses import dataclass
from typing import Optional

from aiogram_scenario.fsm.state import BaseState


@dataclass()
class LockData:

    source_state: BaseState
    destination_state: BaseState
    chat_id: Optional[int]
    user_id: Optional[int]
    is_active: bool
