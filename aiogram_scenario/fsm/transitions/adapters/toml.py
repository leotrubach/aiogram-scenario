try:
    # noinspection PyPackageRequirements
    import toml
except ImportError:
    raise ImportError("""to use this adapter, you need to install «toml»!
More info: https://github.com/uiri/toml#installation""")

from .base import AbstractTransitionsAdapter, RawBaseTransitionsType


class TOMLTransitionsAdapter(AbstractTransitionsAdapter):

    def _parse(self, content: str) -> RawBaseTransitionsType:

        return toml.loads(content)
