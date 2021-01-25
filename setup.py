import setuptools
from pathlib import Path
import re


def fetch_version() -> str:

    content = (Path(__file__).parent / "aiogram_scenario" / "__init__.py").read_text(encoding="UTF-8")
    try:
        version_string = re.findall(r'__version__ = \"\d+\.\d+\.\d+\"', content)[0]
        version = version_string.rsplit(" ", 1)[-1].replace('"', '')
    except IndexError:
        raise RuntimeError("version not found!")

    return version


def fetch_long_description() -> str:

    with open("README.md", encoding="UTF-8") as file_wrapper:
        return file_wrapper.read()


setuptools.setup(
    name="aiogram-scenario",
    version=fetch_version(),
    packages=setuptools.find_packages(exclude=("tests", "docs")),
    url="https://github.com/Abstract-X/aiogram-scenario",
    license="MIT",
    author="Abstract-X",
    author_email="abstract-x-mail@protonmail.com",
    description="FSM implementation for Telegram bots based on aiogram.",
    long_description=fetch_long_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        "aiogram>=2.8,<3.0"
    ],
    include_package_data=True,
    python_requires='>=3.7'
)
