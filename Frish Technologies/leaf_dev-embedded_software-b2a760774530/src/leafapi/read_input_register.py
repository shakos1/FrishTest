from leafapi.request_message import ReadRegistersRequest


class ReadStatusRegisters(object):
    def __init__(self, mpu_addr, register_addr, data_len):
        req = ReadRegistersRequest(mpu_addr=mpu_addr, register_addr=register_addr, data_len=data_len)