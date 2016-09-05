from pathlib import Path
from os import makedirs

from .pairtreeobject import PairTreeObject


class DirectoryPairTreeObjectWriter(object):
    def __init__(self, obj, dir_path):
        self._obj = None
        self._dir_path = None

        self.obj = obj
        self.dir_path = dir_path

    def get_obj(self):
        return self._obj

    def set_obj(self, x):
        if not isinstance(x, PairTreeObject):
            raise TypeError()
        self._obj = x

    def del_obj(self):
        self._obj = None

    def get_dir_path(self):
        return self._dir_path

    def set_dir_path(self, x):
        self._dir_path = Path(x)

    def del_dir_path(self):
        self._dir_path = None

    def write(self):
        for iobs in self.obj.bytestreams:
            iobs_path = Path(self.dir_path, iobs.intraobjectaddress)
            if not iobs_path.parent.exists():
                makedirs(str(iobs_path.parent), exist_ok=True)
            with iobs.openable.open('rb') as src:
                with iobs_path.open('wb') as dst:
                    data = src.read(1024*8)
                    while data:
                        dst.write(data)
                        data = src.read(1024*8)

    dir_path = property(
        get_dir_path, set_dir_path, del_dir_path
    )
    obj = property(
        get_obj, set_obj, del_obj
    )
