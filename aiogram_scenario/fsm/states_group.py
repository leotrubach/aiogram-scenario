from typing import Collection, List

from .state import BaseState


class StatesGroupMixin:

    def __len__(self):

        return len(self.select())

    def __repr__(self):

        return f"<{type(self).__name__} ({', '.join(i.name for i in self.select())})>"

    def __iter__(self):

        return iter(self.select())

    def __contains__(self, state: BaseState):

        return state in self.select()

    def select(self, *, exclude: Collection[BaseState] = ()) -> List[BaseState]:

        states = [i for i in vars(self).values() if isinstance(i, BaseState)]

        if exclude:
            states = list(filter(lambda state: state not in exclude, states))

        return states
