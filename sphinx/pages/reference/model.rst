=====
model
=====

.. currentmodule:: ndf_parse.model

.. automodule:: ndf_parse.model

.. contents:: Table of Contents
    :depth: 3
    :local:

Abstract Classes
----------------

.. autoclass:: DeclListRow 
    :members:    

.. autoclass:: DeclarationsList
    :show-inheritance:
    :members: add, insert

Model Classes
-------------

Row Classes
^^^^^^^^^^^

.. autoclass:: ListRow
    :show-inheritance:

.. autoclass:: MapRow
    :show-inheritance:

.. autoclass:: MemberRow
    :show-inheritance:

.. autoclass:: ParamRow
    :show-inheritance:

List-like Classes
^^^^^^^^^^^^^^^^^

.. autoclass:: List
    :show-inheritance:

    .. method:: by_n(namespace : str) -> ListRow
                by_n(namespace : str, strict : bool) -> Optional[ListRow]
                by_name(namespace : str) -> ListRow
                by_name(namespace : str, strict : bool) -> Optional[ListRow]
    .. automethod:: by_namespace
    
    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace

.. autoclass:: Object
    :show-inheritance:
    
    .. method:: by_n(namespace : str) -> MemberRow
                by_n(namespace : str, strict : bool) -> Optional[MemberRow]
                by_name(namespace : str) -> MemberRow
                by_name(namespace : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_namespace
    
    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace
    
    .. method:: by_m(member : str) -> MemberRow
                by_m(member : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_member

    .. method:: rm_m(member : str)
    .. automethod:: remove_by_member

.. autoclass:: Template
    :show-inheritance:
    
    .. method:: by_n(namespace : str) -> MemberRow
                by_n(namespace : str, strict : bool) -> Optional[MemberRow]
                by_name(namespace : str) -> MemberRow
                by_name(namespace : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_namespace
    
    .. method:: rm_n(namespace : str)
                remove_by_name(namespace : str)
    .. automethod:: remove_by_namespace
    
    .. method:: by_m(member : str) -> MemberRow
                by_m(member : str, strict : bool) -> Optional[MemberRow]
    .. automethod:: by_member

    .. method:: rm_m(member : str)
    .. automethod:: remove_by_member

.. autoclass:: Params
    :show-inheritance:
    
    .. method:: by_p(self, param: str) -> ParamRow
                by_p(self, param: str, strict : bool) -> Optional[ParamRow]
    .. automethod:: by_param
    
    .. method:: rm_p(param : str)
    .. automethod:: remove_by_param

.. autoclass:: Map
    :show-inheritance:
    
    .. method:: by_k(self, key: str) -> MapRow
                by_k(self, key: str, strict : bool) -> Optional[MapRow]
    .. automethod:: by_key
    
    .. method:: rm_k(key : str)
    .. automethod:: remove_by_key

Typing
------

.. data:: CellValue
    :type: type alias

    :class:`List` | :class:`Object` | :class:`Template` | :class:`Map` | `str`
