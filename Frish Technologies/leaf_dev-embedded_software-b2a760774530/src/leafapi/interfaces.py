"""
Leaf API  Interfaces
---------------------

A collection of base classes that are used throughout
the leafapi library.
"""
from multiprocessing import Lock

from leafapi.exceptions import NotImplementedException


class Singleton(object):
    """
    Singleton base class
    http://mail.python.org/pipermail/python-list/2007-July/450681.html
    """
    def __new__(cls, *args, **kwargs):
        """ Create a new instance
        """
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst


class SingletonThreadSafe(type):
    def __new__(mcs, name, bases, attrs):
        # Assume the target class is created (i.e. this method to be called) in the main thread.
        cls = super(SingletonThreadSafe, mcs).__new__(mcs, name, bases, attrs)
        cls.__shared_instance_lock__ = Lock()
        return cls

    def __call__(cls, *args, **kwargs):
        with cls.__shared_instance_lock__:
            try:
                return cls.__shared_instance__
            except AttributeError:
                cls.__shared_instance__ = super(SingletonThreadSafe, cls).__call__(*args, **kwargs)
                return cls.__shared_instance__


class ILeafApiClient(object):

    def read_registers(self, unit, address, count, **kwargs):
        """
        :param unit: The slave unit this request is targeting
        :param address: The starting address to read from
        :param count: The number of registers to read
        :param kwargs: extra args
        :returns: A deferred response handle
        """
        pass

    def write_registers(self, unit, address, count, values, **kwargs):
        """
        :param unit: The slave unit this request is targeting
        :param address: The starting address to write to
        :param count: The number of registers to write
        :param values: The values to write to the specified address. Should be already encoded
        :param kwargs: extra args
        :returns: A deferred response handle
        """
        pass


class IPayloadBuilder(object):
    """
    This is an interface to a class that can build a payload
    for a serial protocol format.
    """

    def build(self):
        """ Return the payload buffer as a list

        This list is two bytes per element and can
        thus be treated as a list of registers.

        :returns: The payload buffer as a list
        """
        raise NotImplementedException("set context values")
