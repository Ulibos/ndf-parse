"""Rudimentary test for scripts in docs. Will simply abort and exit with code 1
if any file encounters an error."""
import os, sys, glob
import argparse
import doctest
import pathlib
import typing as t
import subprocess as sp

PROJ_ROOT = pathlib.Path(__file__).parent.parent.absolute()

SkipFilter = t.Callable[[str], bool]


def line_width():
    return os.get_terminal_size().columns if sys.stdout.isatty() else 79


def as_line(value: str, compensate: int = 0, filler: str = "="):
    return f"{value} ".ljust(line_width() + compensate, filler)


def NOOP(arg: str) -> bool:
    return False


def run_code(path: str) -> int:
    num_fails = 0
    print(f"Testing scripts from {path}:")
    for fpath in glob.glob(path, recursive=True):
        print(as_line(os.path.split(fpath)[1]))
        if sp.call(["python", fpath], stdout=sp.DEVNULL):
            print(as_line("\x1b[31mERROR\x1b[0m", 9))
            num_fails += 1
    return num_fails


def test_snippets(path: str, skip_cond: SkipFilter = NOOP) -> int:
    num_fails = 0
    print(f"Testing snippets in {path}:")
    for fpath in glob.glob(path, recursive=True):
        if skip_cond(fpath):
            continue
        print(as_line(str(fpath)))
        result = doctest.testfile(
            os.path.abspath(fpath),
            optionflags=doctest.NORMALIZE_WHITESPACE,
        )
        if result.failed:
            print(as_line("\x1b[31mERROR\x1b[0m", 9))
            num_fails += result.failed
    return num_fails


parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-code",
    "-c",
    action="store_true",
    help="Disable tests for code in 'sphinx\\pages\\code'",
)
parser.add_argument(
    "--no-docs",
    "-d",
    action="store_true",
    help=(
        "Disable tests for interactive code snippets in docs "
        "(the ones that start with `>>>`)."
    ),
)
parser.add_argument(
    "--no-examples",
    "-e",
    action="store_true",
    help="Disable tests for interactive code snippets in 'ndf_parse'.",
)


if __name__ == "__main__":
    os.chdir(PROJ_ROOT)

    args = parser.parse_args()
    if args.no_code and args.no_docs and args.no_examples:
        raise ValueError("All tests were disabled by passed arguments.")

    # test standalone code examples
    num_fails = 0
    if not args.no_examples:  # adhoc debug switch
        num_fails = run_code("sphinx\\pages\\code\\**\\*.py")

    # test embedded examples in the library
    if not args.no_code:  # adhoc debug switch
        num_fails += test_snippets(
            "ndf_parse\\**\\*.py",
            lambda x: x == "ndf_parse\\__init__.py",  # skip __init__ docs because samples are pseudocode
        )

    # test embedded code examples
    if not args.no_docs:
        num_fails += test_snippets("sphinx\\pages\\**\\*.rst")
        # docs_root = PROJ_ROOT / "sphinx\\pages"
        # os.chdir(docs_root)
        # print("Testing docs snippets:")
        # for _root, dirs, files in os.walk("."):
        #     for fpath in files:
        #         if not fpath.endswith("rst"):
        #             continue
        #         root = pathlib.Path(_root)
        #         fpath = root / fpath
        #         print(as_line(str(fpath)))
        #         result = doctest.testfile(
        #             str(fpath.absolute()),
        #             optionflags=doctest.NORMALIZE_WHITESPACE,
        #         )
        #         if result.failed:
        #             print(as_line("\x1b[31mERROR\x1b[0m", 9))
        #             doc_examples_failed += result.failed

    # done
    sys.exit(num_fails)
