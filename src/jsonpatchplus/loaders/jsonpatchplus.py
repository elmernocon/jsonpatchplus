import json

import yaml
from pathlib import Path
from typing import List

from ..ctypes import (
    StringOrFilePath,
    JsonDocument,
    JsonPatch,
    JsonPatchDocument,
    JsonPatchDocumentLoader,
    JsonPatchPreprocessor,
)
from ..exceptions import JsonPatchInvalidError


class Expansion:
    def __init__(
        self, /, *, tag: str, patch: JsonPatch, expansions: List[JsonPatch]
    ) -> None:
        self.tag = tag
        self.patch = patch
        self.expansions = expansions

    def __str__(self):
        delimiter = "\n- "
        return "[{}]: {} expanded into:{}".format(
            self.tag,
            json.dumps(self.patch),
            delimiter + delimiter.join(json.dumps(e) for e in self.expansions),
        )


class Loader:
    def __init__(
        self,
        /,
        *,
        doc: JsonDocument,
        preprocessors: List[JsonPatchPreprocessor],
        **kwargs,
    ) -> None:
        self.doc = doc
        self.preprocessors = preprocessors

        self.expansions: List[Expansion] = []

    def __call__(self, s_or_fp: StringOrFilePath, /, **kwargs) -> JsonPatchDocument:
        self.expansions = []

        if not isinstance(s_or_fp, (bytes, str)):
            kwargs.setdefault("encoding", "utf-8")
            kwargs.setdefault("errors", "ignore")
            s_or_fp = Path(s_or_fp).read_text(**kwargs)

        if not isinstance(s_or_fp, str):
            raise JsonPatchInvalidError()

        result = yaml.safe_load(s_or_fp)

        if not isinstance(result, list):
            raise JsonPatchInvalidError()

        for preprocessor in sorted(self.preprocessors, key=lambda p: p.priority):
            expanded_result = []
            for patch in result:
                patch_expansions = list(preprocessor(patch=patch, doc=self.doc))
                if not patch_expansions:
                    expanded_result.append(patch)
                    continue
                else:
                    expanded_result.extend(patch_expansions)
                    self.expansions.append(
                        Expansion(
                            tag=preprocessor.tag,
                            patch=patch,
                            expansions=patch_expansions,
                        )
                    )
            result = expanded_result

        return result

    @property
    def logs(self) -> str:
        if self.expansions:
            return "\n".join(str(e) for e in self.expansions)
        else:
            return ""


assert isinstance(Loader, JsonPatchDocumentLoader)


def load(
    s_or_fp: StringOrFilePath,
    /,
    *,
    doc: JsonDocument,
    preprocessors: List[JsonPatchPreprocessor],
    **kwargs,
) -> JsonPatchDocument:
    return Loader(doc=doc, preprocessors=preprocessors)(s_or_fp, **kwargs)


__all__ = [
    "Expansion",
    "Loader",
    "load",
]
