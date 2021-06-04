import logging
import struct
import time
import threading
import serial
from queue import Queue, Empty
from builtins import bytearray

import leafapi.leaf_sys.serial_protocol as sp
from leafapi.exceptions import InvalidMessageReceivedException, LeafTimeoutException, LeafIOException
from leafapi.interfaces import Singleton, SingletonThreadSafe
from leafapi.pdu import ApiRequest

COM_PORT_NAME = '/dev/ttyACM0'
RX_RESPONSE_TIMEOUT = 5


class SerialProtocolInterface(metaclass=SingletonThreadSafe):

    def __init__(self, serial_port=COM_PORT_NAME, baudrate=115200):
        self.log = logging.getLogger('SP')

        # configuration UART port
        self.serial = serial.Serial()
        self.serial.port = serial_port
        self.serial.baudrate = baudrate
        self.serial.timeout = 0.1
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.bytesize = serial.EIGHTBITS

        self.serial.open()
        self.serial.flushInput()
        self.serial.flushOutput()

        self.tx_frame = sp.cvar.tr_frame
        self.rx_frame = sp.cvar.tr_frame
        self.rx_ctrl = sp.cvar.rx_ctrl

        self.log.debug("tx_frame: {}, rx_frame: {}".format(id(self.tx_frame), id(self.rx_frame)))

        self.log.debug("P: {}, P: {}".format(id(sp.sp_get_package_buf(self.rx_frame)), id(sp.sp_get_package_buf(self.rx_frame))))

        self.rx_q = Queue()
        self.rx_thread = threading.Thread(target=self._rx, args=(self.rx_q,))
        self.rx_thread.start()

    def close(self):
        self.serial.close()
        self.rx_thread.join()

    def _rx(self, rx_q: Queue):
        while self.serial.is_open:
            try:
                data = self.serial.read(1)
                if data != b'':
                    rx_q.put(data)
            except TypeError:
                pass

    def write(self, data: (bytearray, bytes)):
        self.log.debug("{}".format(data))
        try:
            self.serial.write(data)
        except serial.SerialException as _ex:
            raise LeafIOException(str(_ex))

    def write_req(self, req: ApiRequest):
        self.write(req.encode(self.tx_frame))

    def read_frame(self, timeout=-1) -> (sp.sp_tr_frame, sp.sp_packet_format):
        self.log.debug("timeout: {}".format(timeout))
        sp.sp_init_rx_ctrl(self.rx_ctrl, self.rx_frame)

        start_time = time.monotonic()

        state = sp.SP_RX_STATE_SOF_LSB
        while state != sp.SP_RX_STATE_DONE:
            try:
                data = self.rx_q.get(timeout=1)
            except Empty:
                if 0 <= timeout < time.monotonic() - start_time:
                    raise LeafTimeoutException("Waiting for frame timeout!")
                else:
                    continue

            self.log.debug("rx: {}".format(data))

            state = sp.sp_add_byte_to_rx_buff(self.rx_ctrl, data[0])

        if state == sp.SP_RX_STATE_DONE:
            ret = sp.sp_validate_frame(self.rx_frame)
            if ret == sp.RET_CODE_SUCCESS:
                return self.rx_frame

        raise InvalidMessageReceivedException("Frame error, rx state: {}".format(state))

    def read_res(self, timeout=RX_RESPONSE_TIMEOUT):
        return self.read_frame(timeout=timeout)

    def send_req(self, packet: sp.sp_packet_format, data: (bytes, None)):
        self.log.debug("packet: {}".format(self.dump_packet(packet, True)))

        if data is None:
            data = bytes()
        sp.packet_to_frame(data, packet, self.tx_frame)
        sp.sp_create_frame(self.tx_frame, sp.get_req_size(packet))

        buffer = bytes(sp.get_tx_size(self.tx_frame))
        ret = sp.frame_to_bytes(buffer, self.tx_frame)
        if ret <= 0:
            self.log.error("Nothing to send, {}".format(ret))
            return

        self.write(buffer)

    def dump_packet(self, packet: sp.sp_packet_format, to_str=False):
        data_str = ''
        if packet.type & sp.SP_PKG_TYPE_ERROR_FLAG:
            data_str = ', data: {}'.format(sp.get_data_prom_packet(packet))

        out_str = "type: {}, mpu_addr: {}, register_addr: {}, data_len: {}".format(
            hex(packet.type), packet.mpu_addr, packet.register_addr, packet.data_len
        ) + data_str
        if to_str:
            return out_str
        self.log.info(out_str)


if __name__ == '__main__':
    format_str = '%(asctime)s %(name)s[%(process)d]:%(filename)s:%(lineno)d %(levelname)s: %(funcName)s: %(message)s'
    logging.basicConfig(format=format_str,
                        level='DEBUG',
                        datefmt='%Y-%m-%d %H:%M:%S')

    import leafapi.leaf_sys.climat_board as cb

    print(cb.get_relay_timeout_mb_addr(cb.RELAY_0))
    print(cb.get_relay_timeout_mb_addr(cb.RELAY_1))
    print(cb.get_pwm_duty_mb_addr(cb.PWM_3))
    print(cb.get_sensor_value_mb_addr(cb.SENSOR_0))

    REQR_EX = bytearray((0xaa, 0x55, 0x06, 0x00, 0x01, 0x05, 0xe8, 0x03, 0x04, 0x00, 0xbf, 0x43))
    REQR_EX_NOT_VALID = bytearray((0xaa, 0x55, 0x06, 0x00, 0x01, 0x05, 0xe8, 0x03, 0x04, 0x00, 0xbf, 0x44))

    print(REQR_EX[0:5])
    print(REQR_EX[5:])

    sp_mod = SerialProtocolInterface()

    packet = sp.sp_packet_format()

    reqr_count = 0
    reqr_res_count = 0
    try:
        while True:
            # sp_mod.serial.write(REQR_EX[0:5])
            # time.sleep(5)
            # sp_mod.serial.write(REQR_EX[5:])
            # try:
            #     res = sp_mod.read_res(timeout=2)
            #     sp_mod.dump_packet(res)
            # except TimeoutError as ex:
            #     print("{}".format(ex))

            # time.sleep(5)
            sp_mod.serial.write(REQR_EX_NOT_VALID)
            try:
                res = sp_mod.read_res(timeout=2)
                sp_mod.dump_packet(res)
            except TimeoutError as ex:
                print("{}".format(ex))

            packet.type = sp.SP_PKG_TYPE_REQR
            packet.mpu_addr = 3
            packet.register_addr = 3001
            packet.data_len = 10

            sp_mod.send_req(packet, None)
            reqr_count += 1
            try:
                res = sp_mod.read_res()
                reqr_res_count += 1

                sp_mod.dump_packet(res)
            except TimeoutError as ex:
                print("{}".format(ex))

            packet.type = sp.SP_PKG_TYPE_REQW
            packet.mpu_addr = 4
            packet.register_addr = 3001
            packet.data_len = 10
            data = struct.pack('> hhlh', 1, 2, 3, 4)

            sp_mod.send_req(packet, data)
            try:
                res = sp_mod.read_res()
                sp_mod.dump_packet(res)
            except TimeoutError as ex:
                print("{}".format(ex))

    except KeyboardInterrupt:
        pass

    sp_mod.close()
    print("reqr_count    : ", reqr_count)
    print("reqr_res_count: ", reqr_res_count)
