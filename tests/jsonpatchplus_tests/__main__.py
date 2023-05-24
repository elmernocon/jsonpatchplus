from functools import cache
from pathlib import Path
from typing import Any, Callable, Optional

import yaml
from deepdiff import DeepDiff

from jsonpatchplus import patch


@cache
def load_data_file(name: str) -> Any:
    test_dir = Path(__file__).parent
    data_dir = test_dir / "data"
    data_path = data_dir / name
    data_text = data_path.read_text()
    data = yaml.safe_load(data_text)
    return data


def test_patch(orig_file: str, patch_file: str, result_file: str) -> None:
    a = load_data_file(orig_file)
    b = load_data_file(patch_file)
    c = load_data_file(result_file)
    d = patch(a, b, None)
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


if __name__ == "__main__":
    main()
