import copy
import json
from io import StringIO
from typing import Any, Optional

import jsonpatch
import jsonpointer

from .ctypes import (
    JsonDocument,
    JsonPatchDocument,
    JsonPatchDocumentLoader,
)
from .exceptions import JsonPatchInvalidError


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


def patch(
    doc: JsonDocument,
    patches: JsonPatchDocument,
    loader: Optional[JsonPatchDocumentLoader],
    max_error_len: int = 256,
) -> JsonDocument:
    doc = copy.deepcopy(doc)
    patch_obj = jsonpatch.JsonPatch(patch=patches)

    # noinspection PyProtectedMember
    for index, op in enumerate(patch_obj._ops):
        try:
            doc = op.apply(obj=doc)
        except (
            jsonpatch.JsonPatchConflict,
            jsonpatch.JsonPatchTestFailed,
            jsonpatch.InvalidJsonPatch,
        ) as error:
            error_str = truncate_str(str(error), length=max_error_len)

            op_str = json.dumps(op.operation)
            op_path = op.operation["path"]
            op_path_parts = op_path.split("/")
            op_path_readable = " | ".join(
                jsonpointer.unescape(p) for p in op_path_parts if p
            )

            bad_patch = "[{}]: {}\n- path: {}".format(
                index,
                op_str,
                op_path_readable,
            )
            all_patches = "\n".join(
                "[{}]: {}".format(i, json.dumps(p)) for i, p in enumerate(patches)
            )

            sio = StringIO()

            # show loader logs
            if loader is not None:
                loader_logs = loader.logs
                if loader_logs:
                    sio.write("\nloader logs:\n{}".format(loader_logs))

            # show target array
            if is_integer(op_path_parts[-1]):
                op_parent_path = "/".join(op_path_parts[:-1])
                try:
                    op_parent_target = jsonptr_resolve(op_parent_path, doc)
                except ValueError:
                    op_parent_target = None
                if op_parent_target is not None and isinstance(op_parent_target, list):
                    op_parent_target_str = json.dumps(op_parent_target, indent=2)
                    sio.write(
                        "\ntarget array ({}):\n{}".format(
                            op_parent_path, op_parent_target_str
                        )
                    )

            raise JsonPatchInvalidError(
                f"\nerror:\n{error_str}\n"
                f"patch:\n{bad_patch}\n"
                f"patches:\n{all_patches}"
                f"{sio.getvalue()}"
            ) from None

    return doc


__all__ = [
    "patch",
]
