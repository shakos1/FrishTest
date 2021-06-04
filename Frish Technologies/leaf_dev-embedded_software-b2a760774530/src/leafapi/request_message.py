"""
Register Reading and Writing Request/Response
"""
import logging
import leafapi.leaf_sys.serial_protocol as sp

from leafapi.pdu import ApiRequest, ApiResponse

_logger = logging.getLogger(__name__)


class ReadRegistersRequest(ApiRequest):
    """
    Base class for reading a register
    """
    def __init__(self, **kwargs):
        """ Initializes a new instance
        """
        ApiRequest.__init__(self, **kwargs)


class ReadRegistersResponse(ApiResponse):
    """
    Base class for responsing to a API request
    """
    def __init__(self, values=None, **kwargs):
        """ Initializes a new instance
        :param values: The values to write to
        """
        ApiResponse.__init__(self, **kwargs)
        self.registers = values or []

    def get_register(self, index):
        """ Get the requested register

        :param index: The indexed register to retrieve
        :returns: The request register
        """
        return self.registers[index]


class WriteRegistersRequest(ApiRequest):
    """
    Base class for reading a register
    """
    def __init__(self, **kwargs):
        """ Initializes a new instance
        :param values: The values to write
        """
        ApiRequest.__init__(self, **kwargs)

        self.r_type = sp.SP_PKG_TYPE_REQW


class WriteRegistersResponse(ApiResponse):
    """
    Base class for responsing to a API request
    """
    def __init__(self, **kwargs):
        """ Initializes a new instance
        :param values: The values to write to
        """
        ApiResponse.__init__(self, **kwargs)
