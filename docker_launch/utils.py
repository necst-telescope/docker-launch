from collections import defaultdict
from typing import Any, Dict, Hashable, List

Object = Dict[Hashable, Any]


def _groupby(objects: List[Object], key: Hashable) -> Dict[str, List[Object]]:
    grouped = defaultdict(lambda: [])
    for obj in objects:
        group_name = obj.get(key, "")
        grouped[group_name].append(obj)
    return grouped
