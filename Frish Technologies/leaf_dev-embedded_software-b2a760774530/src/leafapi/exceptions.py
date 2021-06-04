"""
Leafapi Exceptions
--------------------

Custom exceptions to be used in the leafapi code.
"""


class LeafException(Exception):
    """ Base leaf exception """

    def __init__(self, string):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.string = string

    def __str__(self):
        return 'Leaf Error: %s' % self.string

    @staticmethod
    def is_error():
        """Error"""
        return True


class NotImplementedException(LeafException):
    """ Error resulting from not implemented function """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        message = "[Not Implemented] %s" % string
        LeafException.__init__(self, message)


class LeafIOException(LeafException):
    """ Error resulting from data i/o """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "[Input/Output] %s" % string
        LeafException.__init__(self, self.message)


class LeafTimeoutException(LeafException):
    """ Error waiting from  """

    def __init__(self, string=""):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.message = "[Timeout] %s" % string
        LeafException.__init__(self, self.message)


class ParameterException(LeafException):
    """ Error resulting from invalid parameter """

    def __init__(self, string=""):
        """ Initialize the exception

        :param string: The message to append to the error
        """
        message = "[Invalid Parameter] %s" % string
        LeafException.__init__(self, message)


class NoSuchSlaveException(LeafException):
    """ Error resulting from making a request to a slave
    that does not exist """

    def __init__(self, string=""):
        """ Initialize the exception

        :param string: The message to append to the error
        """
        message = "[No Such Slave] %s" % string
        LeafException.__init__(self, message)


class InvalidMessageReceivedException(LeafException):
    """
    Error resulting from invalid response received or decoded
    """

    def __init__(self, string=""):
        """ Initialize the exception

        :param string: The message to append to the error
        """
        message = "[Invalid Message] %s" % string
        LeafException.__init__(self, message)


class InvalidMessageCreationException(LeafException):
    """
    Error resulting from invalid message creation
    """

    def __init__(self, string=""):
        """ Initialize the exception

        :param string: The message to append to the error
        """
        message = "[Invalid Message] %s" % string
        LeafException.__init__(self, message)
