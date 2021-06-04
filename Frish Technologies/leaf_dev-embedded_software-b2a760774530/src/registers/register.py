import struct

from app_types import BaseType

R = "R"
W = "W"
RW = R + W
ACCESS_MODES = [R, W]

_size_frm = {
    1: 'b', 2: 'h', 4: 'i', 0: ''  # TODO: remove 0 key
}


class RegisterBase(BaseType):
    def __init__(
            self,
            name: str,
            address: int,
            size: int,
            access_type: str,
            value: int = None,
            unit: int = None,
            is_signed: bool = False
    ):
        """
        :param name: Name of register for data
        :param address: Address of first register
        :param size: Size of the register data in bytes
        :param access_type: R or RW (Read - input register, Write - holding register)
        :param value: Register value
        :param unit: Register owner id (mpu_addr)
        :param is_signed: Flag to indicate that value is signed
        """
        self.name = name
        self.address = address
        self.size = size
        self.access_type = access_type
        self.value = value
        self.unit = unit
        self.is_signed = is_signed

        self._encode_frm = '<' + _size_frm[size]


class Register(RegisterBase):
    def __init__(self, **kwargs):
        RegisterBase.__init__(self, **kwargs)
        self.update_frm()

    def update_frm(self):
        if self.is_signed:
            self._encode_frm = self._encode_frm.lower()
        else:
            self._encode_frm = self._encode_frm.upper()

    def encode(self) -> bytes:
        return struct.pack(self._encode_frm, self.value)

    def decode(self, data: bytes):
        self.value = struct.unpack(self._encode_frm, data)[0]
