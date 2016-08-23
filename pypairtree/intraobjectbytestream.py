from uuid import uuid4

from .utils import identifier_to_path


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
