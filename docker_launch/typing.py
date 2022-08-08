import os
from typing import Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


PathLike = Union[os.PathLike, str, bytes]
Literal = Literal
