from typing import List, Dict
from pathlib import Path
import shutil

from aiogram_scenario.transitions_storages.base import AbstractTransitionsStorage


TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATES_FSM_DIR = TEMPLATES_DIR / "fsm"
TEMPLATES_FSM_STATES_DIR = TEMPLATES_FSM_DIR / "states"
TEMPLATES_HANDLERS_DIR = TEMPLATES_DIR / "handlers"

INITIAL_STATE_TEMPLATE_PATH = TEMPLATES_FSM_STATES_DIR / "initial_state.tpl"
STATE_TEMPLATE_PATH = TEMPLATES_FSM_STATES_DIR / "state.tpl"
INIT_STATES_TEMPLATE_PATH = TEMPLATES_FSM_STATES_DIR / "__init__.tpl"
STATES_GROUP_TEMPLATE_PATH = TEMPLATES_FSM_DIR / "states_group.tpl"
INITIALIZE_FSM_TEMPLATE_PATH = TEMPLATES_FSM_DIR / "initialize.tpl"
INIT_FSM_TEMPLATE_PATH = TEMPLATES_FSM_DIR / "__init__.tpl"
COMMON_HANDLERS_TEMPLATE_PATH = TEMPLATES_HANDLERS_DIR / "common.tpl"
REGISTRATION_HANDLERS_TEMPLATE_PATH = TEMPLATES_HANDLERS_DIR / "registration.tpl"
INIT_HANDLERS_TEMPLATE_PATH = TEMPLATES_HANDLERS_DIR / "__init__.tpl"


def _get_module_name_by_state_name(state_name: str, name_only: bool = False) -> str:

    if state_name.lower().endswith("state"):
        state_name = state_name[:-5]

    module_name = ""
    for index, letter in enumerate(state_name):
        module_name += letter.lower()
        if index == (len(state_name) - 1):
            if not name_only:
                module_name += ".py"
            break

        if ((letter.islower() and state_name[index + 1].isupper())
                or
                (((index + 2) <= (len(state_name) - 1)) and state_name[index + 1:index + 3].istitle())):
            module_name += "_"

    return module_name


def _make_fsm_dirs(fsm_dir: Path, fsm_states_dir: Path, handlers_dir: Path):

    fsm_dir.mkdir()
    fsm_states_dir.mkdir()
    handlers_dir.mkdir()


def _create_fsm_folders(app_dir: Path,
                        fsm_dir: Path,
                        fsm_states_dir: Path,
                        handlers_dir: Path,
                        rewrite: bool) -> None:

    app_dir.mkdir(exist_ok=True)
    try:
        _make_fsm_dirs(fsm_dir, fsm_states_dir, handlers_dir)
    except FileExistsError:
        if rewrite:
            shutil.rmtree(str(fsm_dir))
            _make_fsm_dirs(fsm_dir, fsm_states_dir, handlers_dir)
        else:
            raise FileExistsError("you already have an existing FSM structure! "
                                  "If you want to create a new - first delete the old!")


def _create_module(path: Path, content: str):

    with open(str(path), "w") as file:
        file.write(content)


def _get_template_content(template_path: Path) -> str:

    with open(str(template_path)) as file:
        template_content = file.read()

    return template_content


def _create_state_module(path: Path, state: str, handlers: List[str], template_path: Path):

    template_content = _get_template_content(template_path)

    rendered_template = template_content.format(
        handlers="\n\n\n".join(["""async def {name}(event, fsm: FSMTrigger):\n    ...""".format(name=name)
                                for name in handlers]),
        state_name=state
    )

    state_path = path / _get_module_name_by_state_name(state)
    _create_module(state_path, rendered_template)


def _create_init_module(path: Path, template_path: Path):

    template_content = _get_template_content(template_path)

    init_module_path = path / "__init__.py"
    _create_module(init_module_path, template_content)


def _create_states_group_module(path: Path, initial_state: str, states: List[str], states_mapping):

    template_content = _get_template_content(STATES_GROUP_TEMPLATE_PATH)

    states_imports = "\n".join([f"from .states.{states_mapping[i]} import {i}" for i in states])
    states_defining = "\n    ".join(
        [f"{states_mapping[i].upper()} = {i}({'is_initial=True' if initial_state == i else ''})" for i in states]
    )
    rendered_template = template_content.format(
        states_imports=states_imports,
        states_defining=states_defining
    )

    states_group_module_path = path / "states_group.py"
    _create_module(states_group_module_path, rendered_template)


def _create_initialize_module(path: Path,
                              initial_state: str,
                              states_handlers: Dict[str, List[str]],
                              states_mapping: Dict[str, str]):

    template_content = _get_template_content(INITIALIZE_FSM_TEMPLATE_PATH)

    handlers_rows = []
    for state, handlers in states_handlers.items():
        handlers_rows.append(f"# {states_mapping[state].upper()}")
        for handler in handlers:
            handlers_rows.append(f"{states_mapping[state]}.{handler},")
        if state != list(states_handlers.keys())[-1]:
            handlers_rows.append("")
    rendered_template = template_content.format(
        states_modules_imports="from .states import (\n    " + ",\n    ".join(
            [states_mapping[i] for i in states_handlers.keys()]
        ) + ",\n)",
        initial_state=states_mapping[initial_state].upper(),
        handlers="\n            ".join(handlers_rows)
    )

    initialize_module_path = path / "initialize.py"
    _create_module(initialize_module_path, rendered_template)


def _create_handlers_common_module(path: Path):

    template_content = _get_template_content(COMMON_HANDLERS_TEMPLATE_PATH)

    common_module_path = path / "common.py"
    _create_module(common_module_path, template_content)


def _create_handlers_registration_module(path: Path):

    template_content = _get_template_content(REGISTRATION_HANDLERS_TEMPLATE_PATH)

    registration_module_path = path / "registration.py"
    _create_module(registration_module_path, template_content)


def _get_states(transitions):

    states = []
    for source_state in transitions.keys():
        if source_state not in states:
            states.append(source_state)
        for destination_state in transitions[source_state].values():
            if destination_state not in states:
                states.append(destination_state)

    return states


def create_fsm_structure(storage: AbstractTransitionsStorage,
                         initial_state: str,
                         path: str = ".", *,
                         app_name: str = "app",
                         rewrite: bool = False):

    transitions = storage.read()

    path = Path(path)
    app_dir = path / app_name
    fsm_dir = app_dir / "fsm"
    fsm_states_dir = fsm_dir / "states"
    handlers_dir = app_dir / "handlers"

    _create_fsm_folders(app_dir, fsm_dir, fsm_states_dir, handlers_dir, rewrite)

    states = _get_states(transitions)
    states_mapping = {state: _get_module_name_by_state_name(state, name_only=True) for state in states}
    states_handlers = {state: list(transitions[state].keys()) for state in transitions.keys()}

    for state in states:
        if state == initial_state:
            template_path = INITIAL_STATE_TEMPLATE_PATH
        else:
            template_path = STATE_TEMPLATE_PATH
        _create_state_module(fsm_states_dir, state, list(transitions[state].keys()), template_path)
    _create_init_module(fsm_states_dir, INIT_STATES_TEMPLATE_PATH)
    _create_states_group_module(fsm_dir, initial_state, states, states_mapping)
    _create_initialize_module(fsm_dir, initial_state, states_handlers, states_mapping)
    _create_init_module(fsm_dir, INIT_FSM_TEMPLATE_PATH)
    _create_handlers_common_module(handlers_dir)
    _create_handlers_registration_module(handlers_dir)
    _create_init_module(handlers_dir, INIT_HANDLERS_TEMPLATE_PATH)
