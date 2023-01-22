import inspect
import typing
from enum import Enum
from typing import List, get_args, Dict, Optional, get_origin, get_type_hints

from ord_betterproto import ord_classes

"""
dealing with types in ORD messages
"""


class TypeOfTypeHintError(Exception):
    pass


class TypeOfTypeHint(Enum):
    """
    annotations for type hints, a type hint can be one of the following, they are disjoint
    1. a class: builtin literals, ord messages, ord enum
    2. a List[*]
        - this has the class of `typing._GenericAlias`
    3. a Dict[str, *]
        - this has the class of `typing._GenericAlias`
    4. typing.Optional[*]
        - this has the class of `typing._UnionGenericAlias`

    note for List, Dict, and Optional, their classes are different from the +[*] version:
    ```
    List.__class__ == <class 'typing._SpecialGenericAlias'>
    Dict.__class__ == <class 'typing._SpecialGenericAlias'>
    Optional.__class__ == <class 'typing._SpecialForm'>
    ```
    """
    # type hint: class
    BuiltinLiteral = "BuiltinLiteral"
    OrdEnum = "OrdEnum"
    OrdMessage = "OrdMessage"

    # type hint: List[*] assuming elements uni-typed
    ListOrdMessage = "ListOrdMessage"
    # ListOrdEnum = "ListOrdEnum"  # I haven't encountered any of this
    ListBuiltinLiteral = "ListBuiltinLiteral"

    # type hint: Dict[str, *]
    DictOrdMessage = "DictOrdMessage"
    DictBuiltinLiteral = "DictBuiltinLiteral"

    # type hint: Optional[*]
    OptionalLiteral = "OptionalLiteral"


def get_toth(type_hint) -> TypeOfTypeHint:
    """
    get the type of type hints
    maybe trivial: how to type hint a typehint?
    """
    if inspect.isclass(type_hint):
        if type_hint in ord_classes.BuiltinLiteralClasses:
            return TypeOfTypeHint.BuiltinLiteral
        elif type_hint in ord_classes.OrdMessageClasses:
            return TypeOfTypeHint.OrdMessage
        elif type_hint in ord_classes.OrdEnumClasses:
            return TypeOfTypeHint.OrdEnum
    elif type_hint.__class__ == typing._GenericAlias:
        if type_hint.__name__ == List.__name__ and get_origin(type_hint) == list:
            args_tps = get_args(type_hint)
            # check type hint arguments
            if len(args_tps) != 1:
                raise TypeOfTypeHintError(f"type hint for List has len(args) != 1, this is not expected: {args_tps}")
            arg_tp = args_tps[0]
            if not inspect.isclass(arg_tp):
                raise TypeOfTypeHintError(f"the elements of the List are hinted as non-class: {arg_tp}")

            if arg_tp in ord_classes.OrdMessageClasses:  # note this excludes OrdEnum
                return TypeOfTypeHint.ListOrdMessage
            elif arg_tp in ord_classes.BuiltinLiteralClasses:
                return TypeOfTypeHint.ListBuiltinLiteral
            else:
                raise TypeOfTypeHintError(
                    f"the elements of the List are hinted as "
                    f"neither an OrdMessageClass nor a BuiltinLiteralClasses: {arg_tp}"
                )

        elif type_hint.__name__ == Dict.__name__ and get_origin(type_hint) == dict:
            args_tps = get_args(type_hint)
            # check type hint arguments
            if len(args_tps) != 2:
                raise TypeOfTypeHintError(f"type hint for Dict has len(args) != 2, this is not expected: {args_tps}")
            if args_tps[0] != str:
                raise TypeOfTypeHintError(f"the keys of the Dict are hinted as non-str: {args_tps[0]}")
            if not inspect.isclass(args_tps[1]):
                raise TypeOfTypeHintError(f"the values of the Dict are hinted as non-class: {args_tps[1]}")

            arg_tp = args_tps[1]
            if arg_tp in ord_classes.OrdMessageClasses:  # again this excludes OrdEnum
                return TypeOfTypeHint.DictOrdMessage
            elif arg_tp in ord_classes.BuiltinLiteralClasses:
                return TypeOfTypeHint.DictBuiltinLiteral
            else:
                raise TypeOfTypeHintError(
                    f"the valuess of the Dict are hinted as "
                    f"neither an OrdMessageClass nor a BuiltinLiteralClasses: {arg_tp}"
                )

    elif type_hint.__class__ == typing._UnionGenericAlias and type_hint.__name__ == Optional.__name__:
        args_tps = get_args(type_hint)
        if len(args_tps) != 2:
            raise TypeOfTypeHintError(f"type hint for Optional has len(args) != 2, this is not expected: {args_tps}")
        if args_tps[0] not in ord_classes.BuiltinLiteralClasses:
            raise TypeOfTypeHintError(
                f"found an optional field of non-literal class: {args_tps[0]}"
            )
        return TypeOfTypeHint.OptionalLiteral
    raise TypeOfTypeHintError(f"cannot identify TOTH for: {type_hint}")


def get_type_hints_without_private(obj):
    d = dict()
    for k, v in get_type_hints(obj).items():
        if k.startswith("_"):
            continue
        d[k] = v
    return d
