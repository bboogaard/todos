from abc import ABC
from io import BytesIO
from typing import IO, List


class ExportApi(ABC):

    _separator: str = '\n'

    def dump(self) -> IO[bytes]:
        items = self.get_items()
        return BytesIO(self._separator.join(items).encode())

    def load(self, file: IO[bytes]):
        items = file.read().decode().split(self._separator)
        self.save_items(items)

    def get_items(self):
        raise NotImplementedError()

    def save_items(self, items: List[str]):
        raise NotImplementedError()
