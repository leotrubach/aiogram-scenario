from tgbotscenario.asynchronous.scenario import scene

from aiogramscenario.registrars.scene import SceneRegistrar


class BaseScene(scene.BaseScene):

    def register_handlers(self, registrar: SceneRegistrar, data) -> None:

        pass
