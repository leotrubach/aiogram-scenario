from tgbotscenario.asynchronous.scenario.locks.storages import memory

from aiogramscenario.scenario.storages.locks.base import AbstractLockStorage


class MemoryLockStorage(memory.MemoryLockStorage, AbstractLockStorage):

    pass
