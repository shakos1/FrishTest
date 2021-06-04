import logging
import threading
import time

from leafapi.exceptions import LeafTimeoutException, InvalidMessageReceivedException, LeafException
from leafapi.interfaces import ILeafApiClient
from leafapi.request_message import ReadRegistersRequest, ReadRegistersResponse, WriteRegistersResponse, \
    WriteRegistersRequest
from leafapi.serial_protocol import SerialProtocolInterface

default_res_rx_timeout = 5
default_acquire_timeout = -1  # -1 mean forever


class ApiClient(ILeafApiClient):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

        self._sp = SerialProtocolInterface()
        self._lock = threading.Lock()

    def close(self):
        self._sp.close()

    def _execute(self, req, res, timeout):
        if not self._lock.acquire(timeout=timeout[0]):
            raise LeafTimeoutException("Port acquire")
        try:
            self._sp.write_req(req)
            res.decode(self._sp.read_res(timeout=timeout[1]))
        finally:
            self._lock.release()

    def read_registers(self, unit: int, address: int, count: int, **kwargs) -> ReadRegistersResponse:
        timeout = kwargs.get('timeout', (default_acquire_timeout, default_res_rx_timeout))
        self.log.debug("unit: {}, address: {}, count: {}, timeout: {}".format(unit, address, count, timeout))

        req = ReadRegistersRequest(mpu_addr=unit, register_addr=address, data_len=count)
        self.log.debug("{}".format(req))
        res = ReadRegistersResponse(mpu_addr=unit, register_addr=address, data_len=count)

        self._execute(req, res, timeout)

        self.log.debug("{}".format(res))
        return res

    def write_registers(self, unit: int, address: int, count: int, data: bytes, **kwargs) -> WriteRegistersResponse:
        timeout = kwargs.get('timeout', (default_acquire_timeout, default_res_rx_timeout))
        self.log.debug("unit: {}, address: {}, count: {}, data: {}, timeout: {}".format(
            unit, address, count, data, timeout))

        req = WriteRegistersRequest(mpu_addr=unit, register_addr=address, data_len=count, data=data)
        self.log.debug("{}".format(req))
        res = WriteRegistersResponse(mpu_addr=unit, register_addr=address, data_len=count)

        self._execute(req, res, timeout)

        self.log.debug("{}".format(res))
        return res


def test(client, stop_e, d):
    mpu_addr = 0
    reg_addr = 0
    req_count = 0
    res_count = 0
    while not stop_e.is_set():
        try:
            print("START read", d)
            req_count += 1
            res_data = client.read_registers(mpu_addr, 0x2222, 10, timeout=(1, 1))
            res_count += 1
            print("STOP read", d)
            print(d, res_data)

            req_count += 1
            res_data = client.write_registers(d, reg_addr, 12, data=b"1234567890ab")
            res_count += 1
            print(res_data)
        except LeafException as ex:
            print(ex)

        reg_addr += 1

        mpu_addr += 1
        if mpu_addr >= 256:
            mpu_addr = 0

    print(d, f"req: {req_count}, res: {res_count}")


if __name__ == '__main__':
    format_str = '%(asctime)s %(name)s[%(process)d]:%(filename)s:%(lineno)d %(levelname)s: %(funcName)s: %(message)s'
    logging.basicConfig(format=format_str,
                        level='DEBUG',
                        datefmt='%Y-%m-%d %H:%M:%S')

    client = ApiClient()

    stop_e = threading.Event()
    t1 = threading.Thread(target=test, args=(client, stop_e, 10))
    t2 = threading.Thread(target=test, args=(client, stop_e, 20))

    t1.start()
    t2.start()

    mpu_addr = 0
    try:
        while True:
            time.sleep(1)
            # try:
            #     res_data = client.read_registers(mpu_addr, 0x2222, 10)
            #     print(res_data)
            #
            #     res_data = client.write_registers(mpu_addr, 5555, 12, data=b"1234567890ab")
            #     print(res_data)
            # except LeafException as ex:
            #     print(ex)
            #
            # mpu_addr += 1
            # if mpu_addr >= 256:
            #     mpu_addr = 0
    except KeyboardInterrupt:
        pass

    stop_e.set()

    t1.join()
    t2.join()

    client.close()



