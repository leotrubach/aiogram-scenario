import setuptools

import aiogram_scenario


setuptools.setup(
    name="aiogram_scenario",
    version=aiogram_scenario.__version__,
    packages=[
        "aiogram_scenario"
    ],
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
