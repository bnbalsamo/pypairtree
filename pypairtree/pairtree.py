from pathlib import Path
from os import makedirs
from json import dumps
from uuid import uuid4
try:
    from os import scandir
except ImportError:
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("Requires scandir. Update to Python>=3.5 or " +
                          "install the scandir package.")

from .pairtreeobject import PairTreeObject
from .utils import identifier_to_path, path_to_identifier


class PairTree(object):
    def __init__(self, containing_dir=None, root_dir_name="pairtree_root"):
        self._containing_dir = None
        self._root_dir_name = "pairtree_root"
        self._objects = []

        if containing_dir:
            self.containing_dir = containing_dir
        if root_dir_name:
            self.root_dir_name = root_dir_name

    def __repr__(self):
        attr_dict = {
            'pairtree_root': str(self.pairtree_root),
            'objects': [str(x) for x in self.objects],
            'containing_dir': str(self.containing_dir),
            'root_dir_name': str(self.root_dir_name)
        }
        return "<PairTree {}>".format(dumps(attr_dict, sort_keys=True))

    def gather_objects(self):
        if not self.pairtree_root:
            raise AttributeError("In order to gather objects both the " +
                                 "containing directory and the root " +
                                 "directory name must be specified.")
        stack = [x for x in scandir(str(self.pairtree_root))]
        while stack:
            x = stack.pop()
            if x.is_dir() and len(x.name) > 2:
                o = PairTreeObject(
                    identifier=path_to_identifier(
                        Path(x.path).parent, root=self.pairtree_root
                    )
                )
                o.add_dir(x.path, root=x.path)
                self.add_object(o)
            elif x.is_file():
                # Allow files (like namaste tags) in the pairtree_root.
                # If there is an unencapsulated raw file in the pairtree
                # root itself... things have seriously gone wrong.
                if str(Path(x.path).parent) == str(self.pairtree_root):
                    continue
                o = PairTreeObject(
                    identifier=path_to_identifier(
                        Path(x.path).parent, root=self.pairtree_root
                    )
                )
                o.add_file(x.path, root=Path(x.path).parent)
                self.add_object(o)
            else:
                for y in scandir(x.path):
                    stack.append(y)

    def add_file(self, path, objID=None, root=None):
        if not isinstance(path, Path):
            path = Path(str(path))
        if objID is None:
            objID = uuid4().hex
        o = PairTreeObject(identifier=objID)
        o.add_file(path, root=root)
        self.add_object(o)

    def add_dir(self, path, objID=None, root=None):
        if not isinstance(path, Path):
            path = Path(str(path))
        if objID is None:
            objID = uuid4().hex
        o = PairTreeObject(identifier=objID)
        o.add_file(path, root=root)
        self.add_object(o)

    def get_pairtree_root(self):
        if self.containing_dir and self.root_dir_name:
            return Path(self.containing_dir, self.root_dir_name)
        else:
            return None

    def set_objects(self, x):
        while self.objects:
            self.pop_object()
        for i in x:
            self.add_object(i)

    def get_objects(self):
        return self._objects

    def add_object(self, x):
        if not isinstance(x, PairTreeObject):
            raise ValueError()
        self._objects.append(x)

    def pop_object(self):
        return self._objects.pop()

    def get_containing_dir(self):
        return self._containing_dir

    def set_containing_dir(self, x):
        self._containing_dir = x

    def get_root_dir_name(self):
        return self._root_dir_name

    def set_root_dir_name(self, x):
        self._root_dir_name = x

    def write(self, clobber=False, buf=1024*8):
        if not self.pairtree_root:
            raise AttributeError("A containing directory and a pairtree " +
                                 "root directory must be available.")
        makedirs(str(self.pairtree_root), exist_ok=True)
        for x in self.objects:
            pairtreed_path = identifier_to_path(x.identifier,
                                                root=self.pairtree_root)
            makedirs(str(pairtreed_path), exist_ok=True)
            for y in x.bytestreams:
                target_path = Path(pairtreed_path, x.encapsulation,
                                   y.intraobjectaddress)
                if target_path.exists() and not clobber:
                    continue
                elif target_path.exists():
                    # Clobbering
                    pass
                else:
                    makedirs(str(target_path.parent), exist_ok=True)
                    src = y.open('rb')
                    dst = target_path.open('wb')
                    data = src.read(buf)
                    while data:
                        dst.write(data)
                        data = src.read(buf)
                    dst.close()
                    src.close()

    containing_dir = property(get_containing_dir, set_containing_dir)
    root_dir_name = property(get_root_dir_name, set_root_dir_name)
    objects = property(get_objects, set_objects)
    pairtree_root = property(get_pairtree_root)
