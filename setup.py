import setuptools
from pathlib import Path
import re


LIB_NAME = "aiogram-scenario"
PACKAGE_NAME = "aiogram_scenario"
WORK_DIR = Path(__file__).parent


def fetch_version() -> str:

    content = (WORK_DIR / PACKAGE_NAME / "__init__.py").read_text(encoding="UTF-8")
    try:
        version_string = re.findall(r'__version__ = \"\d+\.\d+\.\d+\"', content)[0]
        version = version_string.rsplit(" ")[-1].replace('"', "")
        return version
    except IndexError:
        raise RuntimeError("version not found!")


setuptools.setup(
    name=LIB_NAME,
    version=fetch_version(),
    packages=setuptools.find_packages(exclude=("docs",)),
    url="https://github.com/Abstract-X/aiogram-scenario",
    license="MIT",
    author="Abstract-X",
    author_email="abstract-x-mail@protonmail.com",
    description="FSM implementation for aiogram (2.x).",
    install_requires=[
        "aiogram>=2.8,<3.0"
    ],
    include_package_data=False
)
