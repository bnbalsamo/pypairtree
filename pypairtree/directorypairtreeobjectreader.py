from pathlib import Path
try:
    from os import scandir
except ImportError:
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("Install scandir or upgrade to Python>3.5")

from .pairtreeobject import PairTreeObject
from .intraobjectbytestream import IntraObjectByteStream


class DirectoryPairTreeObjectReader(object):
    def __init__(self, path, identifier=None):
        self._path = None

        self.path = path
        self.identifier = identifier

    def get_path(self):
        return self._path

    def set_path(self, x):
        self._path = Path(x)

    def del_path(self):
        self._path = None

    def read(self):
        obj = PairTreeObject(identifier=self.identifier)
        stack = [x for x in scandir(str(self.path))]
        while stack:
            x = stack.pop()
            if x.is_dir():
                for y in scandir(str(x.path)):
                    stack.append(y)
            elif x.is_file():
                ioa = str(Path(x.path).relative_to(self.path))
                iobs = IntraObjectByteStream(
                    Path(x.path),
                    intraobjectaddress=str(ioa)
                )
                obj.add_bytestream(iobs)
        return obj

    path = property(
        get_path,
        set_path,
        del_path
    )
