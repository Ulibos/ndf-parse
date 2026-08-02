from __future__ import annotations
import typing as t
import os
import pickle
from .model import List

class Cacher:
    DATA = 0
    CACHE = 1
    cache_path: str
    data_path: str
    enabled: bool

    def __init__(self, data_path: str, cache_path: str = "./ndf_cache"):
        self.cache_path = cache_path
        self.data_path = data_path
        self.enabled = False

    def full_path(self, relfpath: str, source: int) -> str:
        root = self.data_path if source == self.DATA else self.cache_path
        return os.path.join(root, relfpath)

    def get_mtime(self, relfpath: str,  source: int) -> t.Union[float, None]:
        fpath = self.full_path(relfpath, source)
        if os.path.exists(fpath):
            return os.path.getmtime(fpath)

    def data_is_newer(self, relfpath: str) -> bool:
        cache_mtime = self.get_mtime(relfpath, self.CACHE)
        if cache_mtime is None:
            return True
        data_mtime = self.get_mtime(relfpath, self.DATA)
        assert data_mtime is not None, \
            (f"Can't find modification time for '{relfpath}', "
             "check if file path is correct.")
        if cache_mtime < data_mtime:
            return True
        return False

    def save_cache(self, relfpath: str, obj: t.Any):
        cache_fpath = self.full_path(relfpath, self.CACHE)
        fdir = os.path.split(cache_fpath)[0]
        os.makedirs(fdir, exist_ok=True)
        with open(cache_fpath, 'wb') as w:
            pickle.dump(obj, w)

    def load_cache(self, relfpath: str) -> List:
        cache_fpath = self.full_path(relfpath, self.CACHE)
        with open(cache_fpath, 'rb') as r:
            return pickle.load(r)