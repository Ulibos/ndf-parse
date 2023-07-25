"""This package is designed for prcessing Eugen Systems ndf files. It allows for
easier code manipulations than out-of-the-box differ for Eugen mods.
"""
from __future__ import annotations
from typing import (
    AnyStr,
    Type,
    Optional,
    List,
    Union,
    Callable,
    Any,
    Iterator,
    Dict,
)
from types import TracebackType
import os, shutil

import tree_sitter
from . import converter
from . import printer
from . import traverser
from . import model

__version__ = "0.1.2"

# 3 places to search for ndf.dll in descending priority order:
# 1. - via env variable NDF_LIB_PATH
lang_path: Optional[str] = os.environ.get("NDF_LIB_PATH", None)
if lang_path is None:
    # 2. - where tree-sitter-cli builds by default
    dev_path = os.path.expanduser(r"~\AppData\Local\tree-sitter\lib\ndf.dll")
    if os.path.exists(dev_path):
        lang_path = dev_path
if lang_path is None:
    # 3. - inside of the package distribution
    lang_path = os.path.join(os.path.dirname(__file__), "bin\\ndf.dll")
    if not os.path.exists(lang_path):
        raise RuntimeError(
            "Could not find ndf.dll in any of default paths. "
            "Please set env variable `NDF_LIB_PATH=path/to/dll` "
            "before running this script."
        )

NDF_LANG = tree_sitter.Language(lang_path, "ndf",)

parser = tree_sitter.Parser()
parser.set_language(NDF_LANG)


class Edit:
    """Holds data about currently edited file.

    Attributes
    ----------
    tree : :data:`~model.CellValue`
        Model of a currently edited tree.
    file_path : str
        Relative path to a destination file. Path should be relative to a mod
        root, i.e. ``GameData/Generated/...``, :ref:`more on that here
        <path-relativeness>`.
    save : bool
        Whether to write out the file after edits are done or not.
    """

    def __init__(self, tree: model.List, file_path: str, save: bool):
        self.tree: model.List = tree
        self.file_path: str = file_path
        self.save: bool = save


class Mod:
    """This class holds links to source and destination mods. It also holds
    methods and wrappers designed to streamline editing, mainly the
    :meth:`edit` method.

    Attributes
    ----------
    mod_src : str
        Path to an unedited source mod. Can be relative to CWD.
    mod_dst : str
        Path to a generated destination mod. Can be relative to CWD.
    edits : list[Edit]
        List of current edits. It tracks nested :meth:`edit` calls and should
        not be edited by hand.
    current_edit : Edit
        Currently active edit.

    Note
    ----

    Paths are relative to an execution path,
    :ref:`more on that here <path-relativeness>`.

    Examples
    --------

        >>> import ndf_parse as ndf
        >>> mod = ndf.Mod('path/to/unedited/mod', 'path/to/generated/mod')
        >>> with mod.edit('GameData/path/to/file.ndf') as source:
        ...     ...  # edits to the source
        >>> # at the end of `with` file gets automatically written out
        None
    """

    def __init__(self, mod_src: str, mod_dst: str):
        self._mod_src: str
        self._mod_dst: str
        self.mod_src = mod_src
        assert os.path.exists(
            self.mod_src
        ), f"Could not find path `{self.mod_src}` (expanded representation)."
        self.mod_dst = mod_dst
        self.edits: List[Edit] = []

    def edit(
        self, file_path: str, save: bool = True, ensure_no_errors: bool = True
    ) -> Mod:
        """Creates a new edit. It is designed to work with ``with`` clause.
        Avoid using it outside of the ``with`` unless you know what you are
        doing.

        Parameters
        ----------
        file_path : str
            File to be edited. Path should be relative to a mod root, i.e.
            ``GameData/Generated/...``, :ref:`more on that here
            <path-relativeness>`.
        save : bool, default=True
            If True then file gets written out at the end of the ``with``
            statement.
        ensure_no_errors : bool, default=True
            Ensures that original ndf code has no syntax errors. Fails if there
            are any and this parameter is True. Be mindful of
            :ref:`checking strictness <checking-strictness>`.

        Returns
        -------
        Mod
            Returns it's parent :class:`Mod` object. Required for ``with``
            statement to work correctly.
        """
        with open(self.__src(file_path), "rb") as r:
            self.edits.append(
                Edit(convert(r.read(), ensure_no_errors), file_path, save)
            )
        return self

    def parse_src(
        self, file_path: str, ensure_no_errors: bool = True
    ) -> model.List:
        """Parses a file from a source mod.

        This function does not write any modified data back to a destination
        file. It's merely a convenience function for retrieving another mod file
        model to fetch some data without risking to write any modifications back
        out.

        Parameters
        ----------
        file_path : str
            Relative path to a source file. Path should be relative to a mod
            root, i.e. ``GameData/Generated/...``, :ref:`more on that here
            <path-relativeness>`.
        ensure_no_errors : bool, optional, default=True
            If on then fails in case there are any syntactic errors in the
            ndf code. Be mindful of :ref:`checking strictness
            <checking-strictness>`.

        Returns
        -------
        ~model.List
            Model representation of the source mod file.
        
        Examples
        --------
        >>> import ndf_parse as ndf
        >>> mod = ndf.Mod('path/to/unedited/mod', 'path/to/generated/mod')
        >>> with mod.edit('GameData/path/to/units_file.ndf') as units:
        ...     # This is a pseudocode, it does not match an actual mod
        ...     # structure, it's intended to only show a possible use case.
        ...     # We up the speed for any unit that has a 155mm weapon.
        ...     weapons = mod.parse_src('GameData/path/to/weapons_file.ndf')
        ...     for unit_row in units:
        ...         weapon_class = unit_row.value.by_member('WeaponClass').value
        ...         weapon_row = weapons.by_namespace(weapon_class)
        ...         if weapon_row.value.by_member('Caliber').value == '155':
        ...             unit = unit_row.value
        ...             speed_row = unit.by_member('Speed')
        ...             speed_row.value += ' * 2'
        """
        with open(self.__src(file_path), "rb") as r:
            tree = convert(r.read(), ensure_no_errors)
        return tree

    def parse_dst(
        self, file_path: str, ensure_no_errors: bool = True
    ) -> model.List:
        """Parses a file from a destination mod.

        This function is identical to :func:`parse_src` in it's functionality
        and intent.

        Parameters
        ----------
        file_path : str
            Relative path to a destination file. Path should be relative to a
            mod root, i.e. ``GameData/Generated/...``, :ref:`more on that here
            <path-relativeness>`.
        ensure_no_errors : bool, optional, default=True
            If on then fails in case there are any syntactic errors in the
            ndf code. Be mindful of :ref:`checking strictness
            <checking-strictness>`.

        Returns
        -------
        ~model.List
            Model representation of the source mod file.
        """
        with open(self.__dst(file_path), "rb") as r:
            tree = convert(r.read(), ensure_no_errors)
        return tree

    def check_if_src_is_newer(self) -> bool:
        """Nukes the destination mod and recreates a pristine copy of the
        destination mod if the source mod is newer (if modification date of the
        source is newer than of the destination).

        Returns
        -------
        bool
            True if the destination mod was rebuilt.
        """
        if not os.path.exists(self.mod_dst):
            self.update_dst()
            return True
        else:
            src_mtime = os.stat(self.mod_src).st_mtime
            dst_mtime = os.stat(self.mod_dst).st_mtime
            if src_mtime > dst_mtime:
                self.update_dst()
                return True
        return False

    def update_dst(self):
        """Forcefully rebuilds a clean version of the destination mod, no checks
        performed."""
        if os.path.exists(self.mod_dst):
            shutil.rmtree(self.mod_dst, ignore_errors=False)
        shutil.copytree(self.mod_src, self.mod_dst)

    # getters, setters
    # mod_src
    @property
    def mod_src(self):
        return self._mod_src

    @mod_src.setter
    def mod_src(self, path: str):
        self._mod_src = self.__expand_path(path)

    # mod_dst
    @property
    def mod_dst(self):
        return self._mod_dst

    @mod_dst.setter
    def mod_dst(self, path: str):
        self._mod_dst = self.__expand_path(path)

    # edit
    @property
    def current_edit(self) -> Optional[Edit]:
        if len(self.edits):
            return self.edits[-1]

    # context manager
    def __enter__(self) -> model.List:
        if not len(self.edits):
            raise TypeError(
                "Cannot edit, no edits present. Try calling "
                "`Mod.edit(local/path/to/file.ndf)`."
            )
        else:
            return self.edits[-1].tree

    def __exit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_value: Optional[Exception],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        if len(self.edits):
            edit = self.edits.pop()
            if edit.save:
                with open(
                    self.__dst(edit.file_path), "w", encoding="utf-8"
                ) as w:
                    printer.format(edit.tree, w)
        return False

    # path utils
    def __expand_path(self, path: str) -> str:
        return os.path.expanduser(os.path.expandvars(path))

    def __src(self, path: str) -> str:
        return os.path.join(self.mod_src, path)

    def __dst(self, path: str) -> str:
        return os.path.join(self.mod_dst, path)


def convert(data: AnyStr, ensure_no_errors: bool = True) -> model.List:  # type: ignore
    """Converts `string`/`byte` data to a :class:`~model.List` object.
    Should be used to parse ndf files as a whole.

    Parameters
    ----------
    data : AnyStr
        ndf code to parse.
    ensure_no_errors : bool, default=True
        If True then fail if ndf code contains syntax errors. Be mindful of
        :ref:`checking strictness <checking-strictness>`.

    Returns
    -------
    ~model.List
        Model representation of a file.
    """
    if isinstance(data, str):
        data: bytes = data.encode()
    tree: tree_sitter.Node = parser.parse(data).root_node
    if ensure_no_errors:
        traverser.check_tree(tree)
    return converter.convert(tree)


def expression(data: AnyStr, ensure_no_errors: bool = True) -> Dict[str, Any]:  # type: ignore
    """Converts `string`/`byte` data to a an expression wrapped in a
    `dict`. Should be used to parse individual expressions for further
    injection into an existing model.

    Parameters
    ----------
    data : AnyStr
        ndf code to parse.
    ensure_no_errors : bool, optional, default=True
        If True then fail if ndf code contains syntax errors. Be mindful of
        :ref:`checking strictness <checking-strictness>`.

    Returns
    -------
    dict
        A `dict` containing an item along with possible extra row attributes.
    
    Examples
    --------

    >>> import ndf_parse as ndf
    >>> src = \"\"\"Obj is Typ(
    ...     Memb1 = "SomeStr"
    ...     Memb2 = 12
    ... )\"\"\"
    >>> source = ndf.convert(src)
    >>> arg = ndf.expression("export A is 12")
    >>> arg
    {'value': '12', 'namespace': 'A', 'visibility': 'export'}
    >>> source.add(**arg)  # ** will deconstruct dict into method's parameters
    List[1](visibility='export', namespace='A', value='12')
    >>> memb = ndf.expression("Memb3 = [1,2,3,Obj2(Memb1 = 5)]")
    >>> memb
    {'value': [List[0](visibility=None, ... }
    >>> source[0].value.add(**memb)
    Object[2](member='Memb3', type=None, ...)
    >>> ndf.printer.print(source)
    Obj is Typ
    (
        Memb1 = "SomeStr"
        Memb2 = 12
        Memb3 =
        [
            1,
            2,
            3,
            Obj2
            (
                Memb1 = 5
            )
        ]
    )
    export A is 12
    
    """
    if isinstance(data, str):
        data: bytes = data.encode()
    tree: tree_sitter.Node = parser.parse(data).root_node
    if ensure_no_errors:
        traverser.check_tree(tree)
    return converter.find_converter(tree.children[0])


WalkerItem = Union[
    model.DeclarationsList[model.DeclListRow_co], model.DeclListRow_co, str
]


def walk(
    item: WalkerItem[model.DeclListRow_co], condition: Callable[[Any], bool],
) -> Iterator[Any]:
    """walk(item, condition)->Iterator
    Recursively walks a model representation of an ndf file.

    Parameters
    ----------
    item : str | :class:`~model.DeclarationsList` | :class:`~model.DeclListRow`
        Source to walk.
    condition : Callable[[Any], bool]
        Function that is responsible for filtering items. Should return True
        if an item matches desired criteria.

        .. note::
            This function can accept multiple types so it's a user's
            responsibility to validate the `item`.

    Yields
    ------
    str | :class:`~model.DeclarationsList` | :class:`~model.DeclListRow`
        Items that match the `condition` criteria (i.e. on which the `condition`
        returns True).
    
    Examples
    --------
    Usage of this function is covered :ref:`here <finding-items>`
    """
    if condition(item):
        yield item
    if isinstance(item, model.DeclListRow):
        for result in walk(item.value, condition):  # type: ignore
            yield result
    if isinstance(item, model.Template):
        for param in item.params:
            for result in walk(param, condition):
                yield result
    if isinstance(item, model.DeclarationsList):
        for row in item:
            for result in walk(row, condition):
                yield result


__all__ = [
    "converter",
    "printer",
    "traverser",
    "convert",
    "expression",
    "parser",
    "Mod",
    "model",
    "walk",
]
