from copy import deepcopy
from typing import Iterator, Optional

import jsonpointer
from jsonpath_ng.ext import parse as jsonpath_parse

from ..ctypes import (
    JsonDocument,
    JsonPatch,
    JsonPatchPreprocessor,
)
from ..exceptions import JsonPatchInvalidError


class JsonPathUnresolvedError(JsonPatchInvalidError):
    pass


class JsonPathPreprocessor:
    original_key: str = "path"
    modify_key: str = "jsonpath"

    def __call__(
        self, /, *, patch: JsonPatch, doc: Optional[JsonDocument] = None, **kwargs
    ) -> Iterator[JsonPatch]:
        if self.modify_key not in patch:
            return
        assert self.original_key not in patch

        jsonpath = patch[self.modify_key]
        jsonpath = jsonpath_parse(path=jsonpath)

        resolved = False
        for match in jsonpath.find(doc):
            resolved = True
            new_path = self.get_full_path(match)
            new_patch = deepcopy(patch)
            new_patch.pop(self.modify_key)
            new_patch[self.original_key] = new_path
            yield new_patch

        if not resolved:
            raise JsonPathUnresolvedError()

    @property
    def priority(self) -> int:
        return 10

    @property
    def tag(self) -> str:
        return "jsonpath"

    @staticmethod
    def get_full_path(match) -> str:
        delimiter = "/"
        full_path = str(match.full_path)
        full_path_parts = full_path.split(".")
        return delimiter + delimiter.join(
            jsonpointer.escape(p.removeprefix("[").removesuffix("]"))
            for p in full_path_parts
        )


assert isinstance(JsonPathPreprocessor, JsonPatchPreprocessor)

__all__ = ["JsonPathPreprocessor"]
