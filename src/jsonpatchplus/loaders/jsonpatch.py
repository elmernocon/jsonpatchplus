from pathlib import Path

import yaml

from ..ctypes import (
    StringOrFilePath,
    JsonPatchDocument,
    JsonPatchDocumentLoader,
)
from ..exceptions import JsonPatchInvalidError


class Loader:
    def __call__(self, s_or_fp: StringOrFilePath, /, **kwargs) -> JsonPatchDocument:
        if not isinstance(s_or_fp, (bytes, str)):
            kwargs.setdefault("encoding", "utf-8")
            kwargs.setdefault("errors", "ignore")
            s_or_fp = Path(s_or_fp).read_text(**kwargs)

        if not isinstance(s_or_fp, str):
            raise JsonPatchInvalidError()

        result = yaml.safe_load(s_or_fp)

        if not isinstance(result, list):
            raise JsonPatchInvalidError()

        return result

    @property
    def logs(self) -> str:
        return ""


assert isinstance(Loader, JsonPatchDocumentLoader)


def load(s_or_fp: StringOrFilePath, /, **kwargs) -> JsonPatchDocument:
    return Loader()(s_or_fp, **kwargs)


__all__ = [
    "Loader",
    "load",
]
