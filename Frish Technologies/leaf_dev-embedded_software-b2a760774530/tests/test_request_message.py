import unittest
from unittest.mock import patch

import leafapi.leaf_sys.serial_protocol as sp
from leafapi.exceptions import InvalidMessageCreationException
from leafapi.leaf_sys.serial_protocol import FRAME_PAYLOAD_SIZE
from leafapi.pdu import ApiRequest, ApiResponse
from leafapi.request_message import ReadRegistersRequest, \
    ReadRegistersResponse, WriteRegistersRequest, WriteRegistersResponse

REQR_EXAMPLE = bytes((0xaa, 0x55, 0x06, 0x00, 0x01, 0x05, 0xe8, 0x03, 0x04, 0x00, 0xbf, 0x43))


class ApiRequestTestCase(unittest.TestCase):

    @patch('leafapi.leaf_sys.serial_protocol.get_tx_size', return_value=FRAME_PAYLOAD_SIZE * 2)
    def test_encode_not_valid_length(self, _p):

        read_req = ApiRequest(mpu_addr=0x05, register_addr=1000, data_len=FRAME_PAYLOAD_SIZE + 1)
        read_req.r_type = sp.SP_PKG_TYPE_REQW
        self.assertRaises(InvalidMessageCreationException, read_req.encode, sp.cvar.tr_frame)


class ReadRegistersRequestTestCase(unittest.TestCase):
    def test_encode(self):
        read_req = ReadRegistersRequest(mpu_addr=0x05, register_addr=1000, data_len=4)
        self.assertEqual(REQR_EXAMPLE, read_req.encode(sp.cvar.tr_frame))


class ApiResponseTestCase(unittest.TestCase):
    def test_decode_reqw_res(self):
        res = ApiResponse()

        tr_frame = sp.cvar.tr_frame
        packet = sp.sp_packet_format()
        packet.type = sp.SP_PKG_TYPE_REQW
        packet.mpu_addr = 2
        packet.register_addr = 0x1234
        packet.data_len = 0

        data = bytes(0)
        sp.packet_to_frame(data, packet, tr_frame)

        res.decode(tr_frame)
        self.assertEqual(sp.SP_PKG_TYPE_REQW, res.r_type)
        self.assertEqual(2, res.mpu_addr)
        self.assertEqual(0x1234, res.register_addr)
        self.assertEqual(0, res.data_len)
        self.assertEqual(sp.SP_ERROR_OK, res.error_code)
        self.assertFalse(res.is_error())

    def test_decode_res_error(self):
        res = ApiResponse()

        tr_frame = sp.cvar.tr_frame
        packet = sp.sp_packet_format()
        packet.type = sp.SP_PKG_TYPE_REQW | sp.SP_PKG_TYPE_ERROR_FLAG
        packet.mpu_addr = 2
        packet.register_addr = 0x1234
        packet.data_len = 1

        data = bytes((sp.SP_ERROR_UNKNOWN,))
        sp.packet_to_frame(data, packet, tr_frame)

        res.decode(tr_frame)
        self.assertEqual(sp.SP_PKG_TYPE_REQW | sp.SP_PKG_TYPE_ERROR_FLAG, res.r_type)
        self.assertEqual(2, res.mpu_addr)
        self.assertEqual(0x1234, res.register_addr)
        self.assertEqual(1, res.data_len)
        self.assertEqual(sp.SP_ERROR_UNKNOWN, res.error_code)
        self.assertTrue(res.is_error())


class ReadRegistersResponseTestCase(unittest.TestCase):
    def test_decode_reqr_res(self):
        res = ReadRegistersResponse()

        tr_frame = sp.cvar.tr_frame
        packet = sp.sp_packet_format()
        packet.type = sp.SP_PKG_TYPE_REQR
        packet.mpu_addr = 2
        packet.register_addr = 0x1234
        packet.data_len = 10

        expected_read_data = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        data = bytes(expected_read_data)
        sp.packet_to_frame(data, packet, tr_frame)

        res.decode(tr_frame)
        self.assertEqual(sp.SP_PKG_TYPE_REQR, res.r_type)
        self.assertEqual(2, res.mpu_addr)
        self.assertEqual(0x1234, res.register_addr)
        self.assertEqual(10, res.data_len)
        self.assertEqual(sp.SP_ERROR_OK, res.error_code)
        self.assertFalse(res.is_error())
        self.assertEqual(bytes(expected_read_data), res.data)


class WriteRegistersRequestTestCase(unittest.TestCase):
    REQW_EXAMPLE = bytes((0xaa, 0x55, 0x0a, 0x00, 0x02, 0x05, 0xe8, 0x03, 0x04, 0x00, 0x01, 0x02, 0x03, 0x04, 0x3e, 0x8d))

    def test_encode(self):
        read_req = WriteRegistersRequest(mpu_addr=0x05, register_addr=1000, data_len=4, data=b'\x01\x02\x03\x04')
        self.assertEqual(self.REQW_EXAMPLE, read_req.encode(sp.cvar.tr_frame))


class WriteRegistersResponseTestCase(unittest.TestCase):

    def test_decode_reqw_res(self):
        tr_frame = sp.cvar.tr_frame
        packet = sp.sp_packet_format()
        packet.type = sp.SP_PKG_TYPE_REQW
        packet.mpu_addr = 2
        packet.register_addr = 0x1234
        packet.data_len = 1
        expected_read_data = (1,)
        data = bytes(expected_read_data)
        sp.packet_to_frame(data, packet, tr_frame)

        res = WriteRegistersResponse()
        res.decode(tr_frame)

        self.assertEqual(sp.SP_PKG_TYPE_REQW, res.r_type)
        self.assertEqual(2, res.mpu_addr)
        self.assertEqual(0x1234, res.register_addr)
        self.assertEqual(1, res.data_len)
        self.assertEqual(sp.SP_ERROR_OK, res.error_code)
        self.assertFalse(res.is_error())
        self.assertEqual(bytes(expected_read_data), res.data)


if __name__ == '__main__':
    unittest.main()
