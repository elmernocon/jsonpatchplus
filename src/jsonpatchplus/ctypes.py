from typing import (
    Any,
    Dict,
    IO,
    Iterator,
    List,
    Optional,
    Union,
)
from typing import (
    Protocol,
    runtime_checkable,
)


StringOrFilePath = Union[str, bytes, IO]
PrimitiveType = Union[bool, int, float, str]
JsonDocument = Union[PrimitiveType, Dict[str, Any], List[Any]]
JsonPatch = Dict[str, Any]
JsonPatchDocument = List[JsonPatch]


# noinspection PyPropertyDefinition
@runtime_checkable
class JsonPatchDocumentLoader(Protocol):
    def __call__(self, s_or_fp: StringOrFilePath, /, **kwargs) -> JsonPatchDocument:
        ...

    @property
    def logs(self) -> str:
        ...


# noinspection PyPropertyDefinition
@runtime_checkable
class JsonPatchPreprocessor(Protocol):
    def __call__(
        self, /, *, patch: JsonPatch, doc: Optional[JsonDocument] = None, **kwargs
    ) -> Iterator[JsonPatch]:
        ...

    @property
    def priority(self) -> int:
        ...

    @property
    def tag(self) -> str:
        ...


__all__ = [
    "StringOrFilePath",
    "PrimitiveType",
    "JsonDocument",
    "JsonPatch",
    "JsonPatchDocument",
    "JsonPatchDocumentLoader",
    "JsonPatchPreprocessor",
]
