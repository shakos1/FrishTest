"""
Contains base classes for Leaf API request/response/error packets
"""
import logging

import leafapi.leaf_sys.serial_protocol as sp
import leafapi.leaf_sys.mb_data as mb_data
from leafapi.exceptions import NotImplementedException, InvalidMessageCreationException

_logger = logging.getLogger(__name__)


class ApiPDU(object):
    def __init__(self, **kwargs):
        """ Initializes the base data for a API request """
        self.r_type = kwargs.get('r_type', sp.SP_PKG_TYPE_REQR)
        self.mpu_addr = kwargs.get('mpu_addr', mb_data.MAIN_BOARD_ADDR)
        self.register_addr = kwargs.get('register_addr', mb_data.MB_IR_FW_VERSION)
        self.data_len = kwargs.get('data_len', 0)
        self.data = kwargs.get('data', bytes())

    def encode(self, tr_frame):
        """ Encodes the message

        :raises: A not implemented exception
        """
        raise NotImplementedException()

    def decode(self, data):
        """ Decodes data part of the message.

        :param data: is a string object
        :raises: A not implemented exception
        """
        raise NotImplementedException()

    def __str__(self):
        _s = "type: {} ({}), mpu_addr: {} ({}), register_addr: {} ({}), data_len: {}".format(
            self.r_type, hex(self.r_type), self.mpu_addr, hex(self.mpu_addr),
            self.register_addr, hex(self.register_addr), self.data_len)
        return _s


class ApiRequest(ApiPDU):
    def __init__(self,  mpu_addr, register_addr, data_len, **kwargs):
        """ Proxy to the lower level initializer """
        ApiPDU.__init__(self, **kwargs)
        self.mpu_addr = mpu_addr
        self.register_addr = register_addr
        self.data_len = data_len

        # self._tr_frame = sp.cvar.tr_frame
        self._packet = sp.sp_packet_format()

    def __str__(self):
        _s = super().__str__()
        return "REQ: {}, data: {}".format(_s, self.data)

    def encode(self, tr_frame) -> bytes:
        """ Encodes the request packet
        Note: data should be already encoded
        :return: The encoded packet
        """
        _logger.debug("encode: tr_frame: {}".format(id(tr_frame), tr_frame))

        self._packet.type = self.r_type
        self._packet.mpu_addr = self.mpu_addr
        self._packet.register_addr = self.register_addr
        self._packet.data_len = self.data_len

        sp.packet_to_frame(self.data, self._packet, tr_frame)

        ret = sp.sp_create_frame(tr_frame, sp.get_req_size(self._packet))
        if ret != sp.SP_ERROR_OK:
            raise InvalidMessageCreationException("sp_create_frame ret {}".format(ret))

        buffer = bytes(sp.get_tx_size(tr_frame))
        ret = sp.frame_to_bytes(buffer, tr_frame)
        if ret <= 0:
            raise InvalidMessageCreationException("frame_to_bytes ret {}".format(ret))

        return buffer


class ApiResponse(ApiPDU):
    """ Base class for a api response PDU """
    def __init__(self, **kwargs):
        """ Proxy to the lower level initializer """
        ApiPDU.__init__(self, **kwargs)
        self.error_code = sp.SP_ERROR_OK

    def is_error(self):
        """Checks if the error is a success or failure"""
        return self.r_type & sp.SP_PKG_TYPE_ERROR_FLAG == sp.SP_PKG_TYPE_ERROR_FLAG

    def __str__(self):
        _s = super().__str__()
        return "RES: {}, error_code: {}, data: {}".format(_s, self.error_code, self.data)

    def decode(self, data: (bytes, sp.sp_tr_frame, sp.sp_packet_format)):
        """ Decode a register response packet header

        :param data: The response to decode
        """
        _logger.debug("data: {}, {}".format(id(data), data))
        if isinstance(data, (sp.sp_tr_frame, sp.sp_packet_format)):
            if isinstance(data, sp.sp_tr_frame):
                _packet = sp.sp_get_package_buf(data)
            else:
                _packet = data
            self.r_type = _packet.type
            self.mpu_addr = _packet.mpu_addr
            self.register_addr = _packet.register_addr
            self.data_len = _packet.data_len

            if self.is_error():
                self.error_code = sp.get_data_prom_packet(_packet)

            self.data = bytes(_packet.data_len)
            ret = sp.packet_data_to_bytes(self.data, _packet)
            if ret < 0:
                _logger.error("packet_data_to_bytes ret {}".format(ret))
        else:
            raise NotImplementedException("decode from bytes is not implemented")
