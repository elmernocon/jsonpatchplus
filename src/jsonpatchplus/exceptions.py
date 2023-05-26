class JsonPatchError(Exception):
    pass


class JsonDocumentMissing(JsonPatchError):
    pass


class JsonPatchInvalidError(JsonPatchError):
    pass


class JsonPatchUnsupportedOperationError(JsonPatchError):
    pass


__all__ = [
    "JsonPatchError",
    "JsonDocumentMissing",
    "JsonPatchInvalidError",
    "JsonPatchUnsupportedOperationError",
]
