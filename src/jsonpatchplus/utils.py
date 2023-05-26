from typing import Any


def is_integer(value: str) -> bool:
    try:
        _ = int(value)
        return True
    except ValueError:
        return False


def jsonptr_escape(value: str) -> str:
    if not isinstance(value, str):
        value = str(value)
    return value.replace("~", "~0").replace("/", "~1")


def jsonptr_unescape(value: str) -> str:
    if not isinstance(value, str):
        value = str(value)
    return value.replace("~1", "/").replace("~0", "~")


def jsonptr_resolve(jsonptr: str, obj: Any) -> Any:
    if obj is None:
        return None
    if not jsonptr:
        return obj
    node = obj
    jsonptr = jsonptr.removeprefix("#").removeprefix("/")
    if not jsonptr:
        return node
    parts = jsonptr.split("/")
    for index, part_key in enumerate(parts):
        if isinstance(node, dict):
            # noinspection PyBroadException
            # pylint: disable=broad-except
            try:
                part_key = jsonptr_unescape(part_key)
                node = node[part_key]
            except:
                return None
        elif isinstance(node, list):
            # noinspection PyBroadException
            # pylint: disable=broad-except
            try:
                part_index = int(part_key)
                node = node[part_index]
            except:
                return None
        else:
            raise ValueError(node)
    return node


def truncate_str(s: str, length: int, suffix: str = "...") -> str:
    final_len = length - len(suffix)
    if len(s) < final_len:
        return s
    return f"{s[:final_len]}{suffix}"


__all__ = [
    "is_integer",
    "jsonptr_escape",
    "jsonptr_unescape",
    "jsonptr_resolve",
    "truncate_str",
]
