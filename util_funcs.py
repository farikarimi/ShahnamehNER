import pickle
import os
import glob
from typing import Any


def pickle_obj(obj: object, path: str) -> None:
    """Serialize the given object and store it at the specified path."""
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def unpickle_obj(path: str) -> Any:
    """Deserialize the object at the specified path and return it."""
    with open(path, 'rb') as pf:
        return pickle.load(pf)


def get_most_recent_file(dir_path: str, prefix: str = '', suffix: str = '') -> str:
    """
    Return the path of the most recent file in the directory at the given path
    with the optionally specified prefix and/or suffix."""
    return max(glob.glob(f'{dir_path}/{prefix}*{suffix}'), key=os.path.getctime)
