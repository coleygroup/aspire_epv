import inspect
from enum import Enum

import ord_betterproto

"""
Groups for classes used in ORD
"""

BuiltinLiteralClasses = [str, float, int, bool, bytes]

OrdClasses = tuple(dict(
    (
        inspect.getmembers(
            ord_betterproto,
            lambda member: inspect.isclass(member) and member.__module__ == ord_betterproto.__name__
        )
    )
).values())

OrdEnumClasses = []
OrdMessageClasses = []
for c in OrdClasses:
    if issubclass(c, Enum):
        OrdEnumClasses.append(c)
    else:
        OrdMessageClasses.append(c)
