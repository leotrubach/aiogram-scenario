import setuptools


setuptools.setup(
    name="aiogram_scenario",
    version="0.0.1",
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
