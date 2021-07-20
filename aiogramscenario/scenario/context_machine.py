from dataclasses import dataclass

from tgbotscenario.asynchronous.scenario import context_machine


@dataclass
class ContextData(context_machine.ContextData):

    pass


class ScenarioMachineContext(context_machine.ScenarioMachineContext):

    pass
