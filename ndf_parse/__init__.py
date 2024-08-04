"""This package is designed for prcessing Eugen Systems ndf files. It allows for
easier code manipulations than out-of-the-box differ for Eugen mods.
"""

from __future__ import annotations
import typing as t
from types import TracebackType
import os, shutil

from . import converter
from . import printer
from . import traverser
from . import model
from .parser import parse

__version__ = "0.2.0"

StrBytes = t.Union[str, bytes]

class Edit:
    """Holds data about currently edited file.

    Attributes
    ----------
    tree : :class:`~model.List`
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
    current_edit : Edit | None
        Currently active edit. In fact this is an alias to ``Mod.edits[-1]``,
        i.e. it's an edit at the top of the stack.
    current_tree : model.List | None
        Tree (a model representation of an ndf file) attribute of a currently
        active edit.

    Note
    ----

    Paths are relative to an execution path,
    :ref:`more on that here <path-relativeness>`.

    Examples
    --------
    .. doctest::
        :skipif: True

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
        self.edits: t.List[Edit] = []

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
        .. doctest::
            :skipif: True

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
        performed.

        Warning
        -------
        Must be used before any edits are applied otherwise they will be
        overwritten by data from source.
        """
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
    def current_edit(self) -> t.Optional[Edit]:
        if len(self.edits):
            return self.edits[-1]

    @property
    def current_tree(self) -> t.Optional[model.List]:
        if len(self.edits):
            return self.edits[-1].tree

    def write_edit(self, edit: Edit, force: bool = True) -> bool:
        """Write given edit to the destination. Return True if data was written
        out.

        An example of writing a bunch of edits if context manager (``with``
        statement) was not used:

        .. doctest::
            :skipif: True

            >>> import ndf_parse as ndf
            >>> mod = ndf.Mod('path/to/unedited/mod', 'path/to/generated/mod')
            >>> # load sources to be edited
            >>> ammo_src = Mod.edit('GameData/../Ammunition.ndf').current_tree
            >>> unit_src = Mod.edit('GameData/../UniteDescriptor.ndf').current_tree
            >>> # load decks for reference only, no need to write out later
            >>> decks_src = Mod.edit('GameData/../Decks.ndf', False).current_tree
            >>> ...  # do stuff here
            >>> for edit in mod.edits:
            >>>     mod.write_edit(edit, False)  # disabled forced write so it
            >>>                                  # does not write `decks_src` out

        Parameters
        ----------
        edit : Edit
            An edit to write out to the destination mod.
        force : bool , default=True
            If True (default) then ignores :attr:`Edit.save` property of the
            edit and writes out always.

        Returns
        -------
            ``True`` if file was written out, ``False`` otherwise.
        """
        if edit.save or force:
            with open(
                self.__dst(edit.file_path), "w", encoding="utf-8"
            ) as w:
                printer.format(edit.tree, w)
            return True
        return False

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
        exc_type: t.Optional[t.Type[Exception]],
        exc_value: t.Optional[Exception],
        exc_traceback: t.Optional[TracebackType],
    ) -> bool:
        if len(self.edits):
            edit = self.edits.pop()
            self.write_edit(edit, False)
        return False

    # path utils
    def __expand_path(self, path: str) -> str:
        return os.path.expanduser(os.path.expandvars(path))

    def __src(self, path: str) -> str:
        return os.path.join(self.mod_src, path)

    def __dst(self, path: str) -> str:
        return os.path.join(self.mod_dst, path)


def convert(
    data: t.Union[str, bytes], ensure_no_errors: bool = True
) -> model.List:
    """Converts `string`/`byte` data to a :class:`~model.List` object.
    Should be used to parse ndf files as a whole.

    Parameters
    ----------
    data : str | bytes
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
        data = data.encode()
    tree = parse(data, ensure_no_errors)
    if isinstance(tree, list):
        traverser.throw_tree_errors(data.decode(), tree, 0)
    return converter.convert(tree)


def expression(data: StrBytes, ensure_no_errors: bool = True) -> t.Dict[str, t.Any]:
    """Converts `string`/`byte` data to a an expression wrapped in a
    `dict`. Should be used to parse individual expressions for further
    injection into an existing model.

    Parameters
    ----------
    data : str | bytes
        ndf code to parse.
    ensure_no_errors : bool, optional, default=True
        If True then fail if ndf code contains syntax errors. Be mindful of
        :ref:`checking strictness <checking-strictness>`.

    Returns
    -------
    DictWrapped
        A `dict` containing an item along with possible extra row attributes.

    Examples
    --------

    >>> import ndf_parse as ndf
    >>> src = '''Obj is Typ(
    ...     Memb1 = "SomeStr"
    ...     Memb2 = 12
    ... )'''
    >>> source = ndf.convert(src)
    >>> arg = ndf.expression("export A is 12")
    >>> arg
    {'value': '12', 'namespace': 'A', 'visibility': 'export'}
    >>> source.add(**arg)  # ** will deconstruct dict into method's parameters
    ListRow[1](value='12', visibility='export', namespace='A')
    >>> memb = ndf.expression("Memb3 = [1,2,3,Obj2(Memb1 = 5)]")
    >>> memb
    {'value': List[ListRow[0](value='1', visibility=None, namespace=None),
    ListRow[1](value='2', visibility=None, namespace=None),
    ListRow[2](value='3', visibility=None, namespace=None),
    ListRow[3](value=Object[MemberRow[0](value='5', member='Memb1',
    type=None, visibility=None, namespace=None)], visibility=None,
    namespace=None)], 'member': 'Memb3'}
    >>> source[0].value.add(**memb)
    MemberRow[2](value=List[ListRow[0](value='1', visibility=None, namespace=None),
    ListRow[1](value='2', visibility=None, namespace=None),
    ListRow[2](value='3', visibility=None, namespace=None),
    ListRow[3](value=Object[MemberRow[0](value='5', member='Memb1', type=None,
    visibility=None, namespace=None)], visibility=None, namespace=None)],
    member='Memb3', type=None, visibility=None, namespace=None)
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
    tree = parse(data, ensure_no_errors)
    if isinstance(tree, list):
        traverser.throw_tree_errors(data, tree)
    return converter.find_converter(tree.children[0])


def expressions(data: StrBytes, ensure_no_errors: bool = True) -> t.List[t.Dict[str, t.Any]]:  # type: ignore
    """Same as :func:`expression`, only outputs a list of expressions instead of
    only the first one.

    data : str | bytes
        ndf code to parse.
    ensure_no_errors : bool, optional, default=True
        If True then fail if ndf code contains syntax errors. Be mindful of
        :ref:`checking strictness <checking-strictness>`.

    Returns
    -------
    list[DictWrapped]
        A `list` of `dict` items containing expressions with additional data.
    """
    tree = parse(data, ensure_no_errors)
    if isinstance(tree, list):
        traverser.throw_tree_errors(data, tree)
    return list(converter.find_converter(x) for x in tree.children)


def show_source_in_error_logs(value: bool):
    traverser.SHOW_SOURCE_IN_ERROR_LOGS = value


WalkerItem = t.Union[model.abc.List[model.abc.GR], model.abc.GR, str]


def walk(
    item: WalkerItem[model.abc.GR],
    condition: t.Callable[[t.Any], bool],
) -> t.Iterator[t.Any]:
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
    Usage of this function is covered :ref:`here <search-tools>`
    """
    if condition(item):
        yield item
    if isinstance(item, model.abc.Row):
        for result in walk(item.value, condition):  # type: ignore
            yield result
    if isinstance(item, model.Template):
        for param in item.params:
            for result in walk(param, condition):
                yield result
    if isinstance(item, model.abc.List):
        for row in item:
            for result in walk(row, condition):
                yield result


__all__ = [
    "converter",
    "printer",
    "traverser",
    "convert",
    "expression",
    "expressions",
    "parser",
    "Mod",
    "model",
    "walk",
]
