import json

from ..ctypes import (
    StringOrFilePath,
    JsonPatchDocument,
    JsonPatchDocumentLoader,
)
from ..exceptions import JsonPatchInvalidError


class Loader:
    def __call__(self, s_or_fp: StringOrFilePath, /, **kwargs) -> JsonPatchDocument:
        if isinstance(s_or_fp, (bytes, str)):
            result = json.loads(s_or_fp, **kwargs)
        else:
            result = json.load(s_or_fp, **kwargs)

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
