"""
pypairtree
"""
from uuid import uuid4
from pathlib import Path
from os import makedirs
from json import dumps
try:
    from os import scandir
except ImportError:
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("Requires scandir. Update to Python>=3.5 or " +
                          "install the scandir package.")

from .utils import identifier_to_path, path_to_identifier, \
    sanitize_string, desanitize_string

__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.2"


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

    def write(self, clobber=False, buf=1024 * 8):
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


class PairTreeObject(object):
    def __init__(self, identifier=None, path=None,
                 root=None, encapsulation=None):
        self._identifier = None
        self._bytestreams = []
        self._encapsulation = None

        self.encapsulation = encapsulation
        if self.encapsulation is None:
            self.encapsulation = "obj"

        if identifier is None:
            if root:
                self.identifier =  \
                    path_to_identifier(
                        path, root=root
                    ).rstrip(self.encapsulation)
            else:
                self.identifier = uuid4().hex
        else:
            self.identifier = identifier

    def __repr__(self):
        x = {'identifier': self.identifier,
             'bytestreams': [str(x) for x in self.bytestreams]}
        return dumps(x)

    def get_identifier(self, raw=False):
        if raw:
            return self._identifier
        return desanitize_string(self._identifier)

    def set_identifier(self, x):
        if not isinstance(x, str):
            raise ValueError()
        self._identifier = sanitize_string(x)

    def get_bytestreams(self):
        return self._bytestreams

    def set_bytestreams(self, x):
        while self.bytestreams:
            self.pop_bytestream()
        for y in x:
            self.add_bytestream(x)

    def add_bytestream(self, x):
        if not isinstance(x, IntraObjectByteStream):
            raise ValueError()
        for b in self.bytestreams:
            if x.intraobjectaddress == b.intraobjectaddress:
                raise ValueError("Intraobject identifier collision!")
        self._bytestreams.append(x)

    def pop_bytestream(self, x):
        return self._bytestreams.pop()

    def get_encapsulation(self):
        return self._encapsulation

    def set_encapsulation(self, x):
        self._encapsulation = x

    def add_dir(self, path, root=None):
        if not isinstance(path, Path):
            path = Path(str(path))
        if not path.is_dir():
            raise ValueError("{} is not a directory!".format(str(path)))
        else:
            stack = [x for x in scandir(str(path))]
            while stack:
                x = stack.pop()
                if x.is_dir():
                    for y in scandir(x.path):
                        stack.append(y)
                else:
                    if root is None:
                        self.add_bytestream(
                            IntraObjectByteStream(
                                Path(x.path),
                                intraobjectaddress=str(
                                    Path(x.path).relative_to(path)
                                )
                            )
                        )
                    else:
                        self.add_bytestream(
                            IntraObjectByteStream(
                                Path(x.path),
                                intraobjectaddress=str(
                                    Path(x.path).relative_to(root)
                                )
                            )
                        )

    def add_file(self, path, root=None):
        if not isinstance(path, Path):
            path = Path(path)
        if not path.is_file():
            raise ValueError("{} is not a file!".format(str(path)))
        if root is None:
            self.add_bytestream(
                IntraObjectByteStream(
                    path,
                    intraobjectaddress=str(path.relative_to(path.parent))
                )
            )
        else:
            self.add_bytestream(
                IntraObjectByteStream(
                    path,
                    intraobjectaddress=str(path.relative_to(root))
                )
            )

    identifier = property(get_identifier, set_identifier)
    encapsulation = property(get_encapsulation, set_encapsulation)
    bytestreams = property(get_bytestreams, set_bytestreams)


class IntraObjectByteStream(object):
    def __init__(self, openable, intraobjectaddress=None):
        self._openable = None
        self._intraobjectaddress = None

        self.openable = openable
        if intraobjectaddress is None:
            self.intraobjectaddress = identifier_to_path(uuid4().hex)
        else:
            self.intraobjectaddress = intraobjectaddress

    def __repr__(self):
        return str(self.intraobjectaddress)

    def get_openable(self):
        return self._openable

    def set_openable(self, x):
        try:
            o = getattr(x, 'open')
            assert(callable(o))
        except:
            raise ValueError("Openable must provide an 'open' method")
        self._openable = x

    def open(self, *args, **kwargs):
        return self.openable.open(*args, **kwargs)

    def close(self):
        self.openable.close()

    def get_intraobjectaddress(self):
        return self._intraobjectaddress

    def set_intraobjectaddress(self, x):
        self._intraobjectaddress = x

    intraobjectaddress = property(get_intraobjectaddress,
                                  set_intraobjectaddress)
    openable = property(get_openable, set_openable)
