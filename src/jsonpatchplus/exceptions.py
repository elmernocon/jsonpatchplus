class JsonPatchError(Exception):
    pass


class JsonPatchInvalidError(JsonPatchError):
    pass


class JsonPatchUnsupportedOperationError(JsonPatchError):
    pass


__all__ = [
    "JsonPatchError",
    "JsonPatchInvalidError",
    "JsonPatchUnsupportedOperationError",
]
