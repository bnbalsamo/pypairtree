from uuid import uuid4
from pathlib import Path
from json import dumps
try:
    from os import scandir
except ImportError:
    try:
        from scandir import scandir
    except ImportError:
        raise ImportError("Requires scandir. Update to Python>=3.5 or " +
                          "install the scandir package.")

from .utils import sanitize_string
from .utils import desanitize_string
from .utils import path_to_identifier
from .intraobjectbytestream import IntraObjectByteStream


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
