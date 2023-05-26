from functools import cache
from pathlib import Path
from typing import Any, Callable, Optional

import yaml
from deepdiff import DeepDiff

from jsonpatchplus import load, patch
from jsonpatchplus.ctypes import JsonPatchDocumentLoader
from jsonpatchplus.loaders.jsonpatchplus import Loader
from jsonpatchplus.preprocessors.jsonpath import JsonPathPreprocessor


@cache
def load_data_file(name: str) -> Any:
    test_dir = Path(__file__).parent
    data_dir = test_dir / "data"
    data_path = data_dir / name
    data_text = data_path.read_text()
    data = yaml.safe_load(data_text)
    return data


@cache
def load_patch_file(name: str, loader: Optional[JsonPatchDocumentLoader] = None) -> Any:
    test_dir = Path(__file__).parent
    data_dir = test_dir / "data"
    data_path = data_dir / name
    data = load(data_path, loader=loader)
    return data


def test_patch(orig_file: str, patch_file: str, result_file: str, loader: Optional[JsonPatchDocumentLoader] = None) -> None:
    a = load_data_file(orig_file)
    if loader:
        setattr(loader, "doc", a)
    b = load_patch_file(patch_file, loader=loader)
    if loader:
        print(loader.logs)
    c = load_data_file(result_file)
    d = patch(a, b, loader=loader)
    e = DeepDiff(c, d)
    assert not e, e


# noinspection PyBroadException
def expect_exception(
    func: Callable,
    /,
    *args,
    exception_class_name: Optional[str] = None,
    print_error: bool = False,
    **kwargs
) -> None:
    did_raise = False

    try:
        func(*args, **kwargs)
    except Exception as error:
        did_raise = True
        error_type = error.__class__.__name__
        if exception_class_name and not error_type == exception_class_name:
            raise Exception(f"ExceptionTypeMismatch: expected {exception_class_name} but got {error_type}") from None
        if print_error:
            print(f"found expected exception: {error}")

    if not did_raise:
        raise Exception("ExceptionNotRaised")


def main():
    test_patch("original.yaml", "patch1.yaml", "result1.yaml")
    expect_exception(
        test_patch, "list.yaml", "patch2.yaml", "result2.yaml",
        exception_class_name="JsonPatchInvalidError",
    )

    plus_loader = Loader(
        preprocessors=[
            JsonPathPreprocessor()
        ]
    )
    test_patch("deeplist.yaml", "patch3.yaml", "result3.yaml", loader=plus_loader)


if __name__ == "__main__":
    main()
