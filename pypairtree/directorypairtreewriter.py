from pathlib import Path
from os import makedirs

from .pairtree import PairTree
from .directorypairtreeobjectwriter import DirectoryPairTreeObjectWriter
from .utils import identifier_to_path


class DirectoryPairTreeWriter(object):
    def __init__(self, pairtree, containing_dir,
                 root_dir_name="pairtree_root", identifier_prefix=None,
                 objwriter=DirectoryPairTreeObjectWriter):
        self._pairtree = None
        self._containing_dir = None
        self._root_dir_name = None
        self._identifier_prefix = None
        self._objwriter = None

        self.pairtree = pairtree
        self.containing_dir = containing_dir
        self.root_dir_name = root_dir_name
        self.identifier_prefix = identifier_prefix
        self.objwriter = objwriter

    def get_pairtree(self):
        return self._pairtree

    def set_pairtree(self, x):
        if not isinstance(x, PairTree):
            raise TypeError()
        self._pairtree = x

    def del_pairtree(self):
        self._pairtree = None

    def get_containing_dir(self):
        return self._containing_dir

    def set_containing_dir(self, x):
        try:
            x = Path(x)
        except Exception as e:
            raise TypeError(str(e))
        if not x.is_absolute():
            raise ValueError()
        self._containing_dir = x

    def del_containing_dir(self):
        self._containing_dir = None

    def get_root_dir_name(self):
        return self._root_dir_name

    def set_root_dir_name(self, x):
        if not isinstance(x, str):
            raise TypeError()
        self._root_dir_name = x

    def del_root_dir_name(self):
        self._root_dir_name = None

    def get_identifier_prefix(self):
        return self._identifier_prefix

    def set_identifier_prefix(self, x):
        if not isinstance(x, str) and x is not None:
            raise TypeError(str(type(x)))
        self._identifier_prefix = x

    def del_identifier_prefix(self):
        self._identifier_prefix = None

    def get_objwriter(self):
        return self._objwriter

    def set_objwriter(self, x):
        self._objwriter = x

    def del_objwriter(self):
        self._objwriter = None

    def write(self, mkdirs=True):
        pt_dir = Path(self.containing_dir, self.root_dir_name)
        if not pt_dir.is_dir():
            if mkdirs:
                makedirs(str(pt_dir), exist_ok=True)
        else:
            raise ValueError()

        if self.identifier_prefix:
            # Be sure we aren't going to mangle any identifiers
            for x in self.pairtree.objects:
                if not x.identifier.startswith(self.identifier_prefix):
                    raise ValueError()
            # Then write
            with open(str(self.containing_dir), 'w') as f:
                f.write(self.identifier_prefix)

        for obj in self.pairtree.objects:
            obj_id = obj.identifier
            if self.identifier_prefix:
                obj_id = obj.identifier.lstrip(self.identifier_prefix)
            print("ID: {}".format(obj_id))
            obj_path = identifier_to_path(obj_id,
                                          root=pt_dir)
            print("PATH: {}".format(obj_path))
            obj_path = Path(obj_path, obj.encapsulation)
            makedirs(str(obj_path), exist_ok=True)
            o_writer = self.objwriter(obj, obj_path)
            o_writer.write()

    pairtree = property(
        get_pairtree, set_pairtree, del_pairtree
    )
    containing_dir = property(
        get_containing_dir, set_containing_dir, del_containing_dir
    )
    root_dir_name = property(
        get_root_dir_name, set_root_dir_name, del_root_dir_name
    )
    identifier_prefix = property(
        get_identifier_prefix, set_identifier_prefix, del_identifier_prefix
    )
