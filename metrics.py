import sys
import uuid
import pickle
from pathlib import Path


def get_mem_size(obj, seen=None):
    """Recursively finds size of objects (in bytes)"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_mem_size(v, seen) for v in obj.values()])
        size += sum([get_mem_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_mem_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_mem_size(i, seen) for i in obj])
    return size


def get_mem_size_kb(obj, seen=None):
    """Recursively finds size of objects (in KB)"""
    return get_mem_size(obj, seen) / 1024


def get_persisted_size(obj):
    """Get the size of the object (in bytes) after it has been persisted to disk."""
    id = uuid.uuid4()
    path = Path("/tmp") / str(id)
    path = path.with_suffix(".pkl")
    pickle.dump(obj, open(path, "wb"))
    size = path.stat().st_size
    path.unlink()
    return size


def get_persisted_size_kb(obj):
    """Get the size of the object (in KB) after it has been persisted to disk."""
    return get_persisted_size(obj) / 1024


__all__ = [
    "get_mem_size",
    "get_mem_size_kb",
    "get_persisted_size",
    "get_persisted_size_kb",
]
