from pathlib import Path
try:
    from os import scandir
except ImportError:
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("Install scandir or upgrade to Python>3.5")

from .pairtree import PairTree
from .pairtreeobject import PairTreeObject
from .directorypairtreeobjectreader import DirectoryPairTreeObjectReader
from .utils import path_to_identifier


class DirectoryPairTreeReader(object):
    def __init__(self, pairtree_dir,
                 object_reader=DirectoryPairTreeObjectReader):
        self._object_reader = None
        self._pairtree_dir = None

        self.pairtree_dir = pairtree_dir
        self.object_reader = object_reader

    def get_pairtree_dir(self):
        return self._pairtree_dir

    def set_pairtree_dir(self, x):
        p = Path(x)
        if not p.is_dir():
            raise ValueError('Not a dir!')
        self._pairtree_dir = p

    def get_pairtree_root(self):
        return self.pairtree_dir.name

    def get_containing_dir(self):
        return self.pairtree_dir.parent

    def del_pairtree_dir(self):
        self._pairtree_dir = None

    def read(self):
        # This function uses scandir instead of pathlib.Path.iterdir for
        # speed improvements in large directory structures
        p = PairTree()
        id_prefix_file = Path(self.containing_dir, "pairtree_prefix")
        id_prefix = None
        if id_prefix_file.exists():
            with open(str(id_prefix_file), 'r') as f:
                id_prefix = f.read().rstrip("\n")
        stack = [x for x in scandir(str(self.pairtree_dir))]
        while stack:
            x = stack.pop()
            if x.is_dir() and len(x.name) > 2:
                obj_id = path_to_identifier(
                    Path(x.path).relative_to(self.pairtree_dir)
                )
                if id_prefix:
                    obj_id = id_prefix + obj_id
                if self.object_reader:
                    r = self.object_reader(
                        x.path,
                        id_prefix=id_prefix,
                        identifier=obj_id
                    )
                    o = r.read()
                else:
                    o = PairTreeObject(identifier=obj_id)
                p.add_object(o)
            elif x.is_file():
                raise ValueError("Unencapsulated file in the pairtree: " +
                                 "{}".format(x.path))
            else:
                for y in scandir(x.path):
                    stack.append(y)
        return p

    pairtree_dir = property(
        get_pairtree_dir,
        set_pairtree_dir,
        del_pairtree_dir
    )

    pairtree_root = property(
        get_pairtree_root,
    )
    containing_dir = property(
        get_containing_dir,
    )
