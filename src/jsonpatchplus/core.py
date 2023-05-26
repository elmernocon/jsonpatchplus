import copy
import json
from io import StringIO
from typing import Any, Optional

import jsonpatch
import jsonpointer

from .ctypes import (
    StringOrFilePath,
    JsonDocument,
    JsonPatchDocument,
    JsonPatchDocumentLoader,
)
from .exceptions import JsonPatchInvalidError
from .loaders.jsonpatch import Loader
from .utils import (
    is_integer,
    jsonptr_resolve,
    truncate_str,
)


def load(
    s_or_fp: StringOrFilePath, /, *, loader: Optional[JsonPatchDocumentLoader] = None
) -> Any:
    if loader is None:
        loader = Loader()
    data = loader(s_or_fp)
    return data


def patch(
    doc: JsonDocument,
    patches: JsonPatchDocument,
    loader: Optional[JsonPatchDocumentLoader] = None,
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
    "load",
    "patch",
]
