from typing import Dict, Union, Set, Tuple, List, Collection
from pathlib import Path
import shutil
import string

try:
    from jinja2 import Environment  # noqa
except ImportError:
    raise ImportError("""In order to use the code generator, you must install the Jinja2!
More: https://jinja.palletsprojects.com/en/2.11.x/intro/#installation""")

from aiogram_scenario import exceptions


def _get_transitions_items(transitions: Dict[str, Dict[str, str]]) -> Tuple[List[str], Set[str]]:

    states = [source_state for source_state in transitions]
    handlers = set()
    for source_state in transitions:
        for handler in transitions[source_state]:
            destination_state = transitions[source_state][handler]
            if destination_state not in states:
                states.append(destination_state)
            handlers.add(handler)

    return states, handlers


def _get_handlers_relationships(transitions: Dict[str, Dict[str, str]],
                                handlers: Set[str]) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:

    private_relationships = {state: [] for state in transitions}
    common_relationships = {handler: [] for handler in handlers}

    for handler in handlers:
        possesing_states = set()
        for source_state in transitions:
            for handler_ in transitions[source_state]:
                if handler == handler_:
                    possesing_states.add(source_state)

        if len(possesing_states) > 1:
            common_relationships[handler].extend(possesing_states)
        else:
            private_relationships[possesing_states.pop()].append(handler)

    return private_relationships, common_relationships


def _get_state_module_name(state: str) -> str:

    if state.endswith("State"):
        state_name = state[:-5]  # SomeState -> Some
    else:
        state_name = state

    parts = []
    start_index = 0
    for index, letter in enumerate(state_name):
        try:
            next_letter = state_name[index + 1]
            if (
                ((letter not in string.digits) and (next_letter in string.digits))
                or
                ((letter in string.digits) and (next_letter not in string.digits))
                or
                (letter.islower() and next_letter.isupper())
                or
                (letter.isupper() and next_letter.isupper() and state_name[index + 2].islower())
            ):
                parts.append(state_name[start_index:index + 1])
                start_index = index + 1
        except IndexError:
            parts.append(state_name[start_index:])
            break

    module_name = "_".join([i.lower() for i in parts])

    return module_name


def _create_module(path: Path, name: str, content: str = "", *, rewrite: bool = False) -> None:

    module_path = path / name
    if not rewrite and module_path.exists():
        raise exceptions.CodeGenerationError(f"module '{module_path}' already exists!")

    with open(str(path / f"{name}.py"), "w", encoding="UTF-8") as file_wrapper:
        file_wrapper.write(content)


def _create_package(path: Path, init_content: str = "", *, rewrite: bool = False) -> None:

    if path.exists():
        if rewrite:
            shutil.rmtree(str(path))
        else:
            raise exceptions.CodeGenerationError(f"package path '{path}' already exists!")

    path.mkdir()
    _create_module(path, "__init__", init_content, rewrite=rewrite)


class CodeGenerator:

    def __init__(self, environment: Environment):

        self._environment = environment

    def generate_structure(self, app_path: Union[str, Path], initial_state: str,
                           transitions: Dict[str, Dict[str, str]], *, rewrite: bool = False) -> None:

        app_dir = Path(app_path).absolute()  # app/
        fsm_dir = app_dir / "fsm"  # app/fsm/
        states_dir = fsm_dir / "states"  # app/fsm/states/

        self._create_packages(app_dir, fsm_dir, states_dir, rewrite=rewrite)

        states, handlers = _get_transitions_items(transitions)
        private_handlers_relationships, common_handlers_relationships = _get_handlers_relationships(transitions,
                                                                                                    handlers)
        states_modules = {}
        for state in states:
            module_name = self._create_state_module(path=states_dir, state=state, is_initial=state == initial_state,
                                                    handlers=private_handlers_relationships[state])
            states_modules[state] = module_name

        self._create_states_group(fsm_dir, states_modules)
        self._create_common_handlers_module(fsm_dir, list(common_handlers_relationships))
        self._create_initialize_module(fsm_dir, states_modules[initial_state])
        self._create_main_module(app_dir, app_path.name)

    def _create_packages(self, app_dir: Path, fsm_dir: Path, states_dir: Path, *, rewrite: bool = False) -> None:

        packages = {
            app_dir: "__init__",
            fsm_dir: "fsm/__init__",
            states_dir: "fsm/states/__init__"
        }
        for package_path, init_path in packages.items():
            init_content = self._render_template(init_path)
            _create_package(package_path, init_content, rewrite=rewrite)

    def _create_state_module(self, path: Path, state: str, is_initial: bool, handlers: Collection[str]) -> str:

        module_name = _get_state_module_name(state)
        content = self._render_template("fsm/states/state", handlers_names=handlers,
                                        state_name=state, is_initial=is_initial)
        _create_module(path, module_name, content)

        return module_name

    def _create_states_group(self, path: Path, states_modules: Dict[str, str]) -> None:

        content = self._render_template("fsm/states_group", states_modules=states_modules)
        _create_module(path, "states_group", content)

    def _create_common_handlers_module(self, path: Path, handlers: Collection[str]) -> None:

        content = self._render_template("fsm/common_handlers", handlers_names=handlers)
        _create_module(path, "common_handlers", content)

    def _create_initialize_module(self, path: Path, initial_state_module: str) -> None:

        content = self._render_template("fsm/initialize", initial_state_name=initial_state_module)
        _create_module(path, "initialize", content)

    def _create_main_module(self, path: Path, app: str) -> None:

        content = self._render_template("__main__", app_name=app)
        _create_module(path, "__main__", content)

    def _render_template(self, name: str, *args, **kwargs) -> str:

        template = self._environment.get_template(f"{name}.jinja2")
        content = template.render(*args, **kwargs)

        return content
