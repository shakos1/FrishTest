import unittest
import leafapi.leaf_sys.mb_data as mb_data
from registers.sys_registers import InputRegisters, HoldingRegisters
from registers.register import Register, R, RW


class RegistersDescriptionTestCase(unittest.TestCase):
    def test_InputRegisters(self):
        reg = InputRegisters.FW_VERSION
        self.assertEqual(reg.name, "FW_VERSION")
        self.assertEqual(reg.size, mb_data.MB_IR_FW_VERSION_SIZE * 2)
        self.assertEqual(reg.size, 2)
        self.assertEqual(reg.address, mb_data.MB_IR_FW_VERSION)
        self.assertEqual(reg.address, 1000)
        self.assertEqual(reg.access_type, R)

        reg = InputRegisters.GLOBAL_STATUS
        self.assertEqual(reg.name, "GLOBAL_STATUS")
        self.assertEqual(reg.size, mb_data.MB_IR_GLOBAL_STATUS_SIZE * 2)
        self.assertEqual(reg.size, 4)
        self.assertEqual(reg.address, mb_data.MB_IR_GLOBAL_STATUS)
        self.assertEqual(reg.address, 1003)
        self.assertEqual(reg.access_type, R)

        reg = InputRegisters.TACHO_15_VALUE
        self.assertEqual(reg.name, "TACHO_15_VALUE")
        self.assertEqual(reg.size, mb_data.MB_IR_TACHO_15_VALUE_SIZE * 2)
        self.assertEqual(reg.size, 2)
        self.assertEqual(reg.address, mb_data.MB_IR_TACHO_15_VALUE)
        self.assertEqual(reg.address, 1033)
        self.assertEqual(reg.access_type, R)

    def test_HoldingRegisters(self):
        reg = HoldingRegisters.ADDR
        self.assertEqual(reg.name, "ADDR")
        self.assertEqual(reg.size, mb_data.MB_HR_ADDR_SIZE * 2)
        self.assertEqual(reg.size, 2)
        self.assertEqual(reg.address, mb_data.MB_HR_ADDR)
        self.assertEqual(reg.address, 3900)
        self.assertEqual(reg.access_type, RW)

        reg = HoldingRegisters.PWM_15_DUTY_CYCLE
        self.assertEqual(reg.name, "PWM_15_DUTY_CYCLE")
        self.assertEqual(reg.size, mb_data.MB_HR_PWM_15_DUTY_CYCLE_SIZE * 2)
        self.assertEqual(reg.size, 2)
        self.assertEqual(reg.address, mb_data.MB_HR_PWM_15_DUTY_CYCLE)
        self.assertEqual(reg.address, 4057)
        self.assertEqual(reg.access_type, RW)


class RegisterDescriptionTestCase(unittest.TestCase):
    def test_encode(self):
        reg = Register(name="REG1", address=1, size=1, access_type=R, value=0x01)
        buff = reg.encode()
        self.assertEqual(b"\x01", buff)

        reg = Register(name="REG1", address=1, size=2, access_type=R, value=0x0201)
        buff = reg.encode()
        self.assertEqual(b"\x01\x02", buff)

        reg = Register(name="REG1", address=1, size=4, access_type=R, value=0x04030201)
        buff = reg.encode()
        self.assertEqual(b"\x01\x02\x03\x04", buff)

        reg = Register(name="REG1", address=1, size=1, access_type=R, value=-1, is_signed=True)
        buff = reg.encode()
        self.assertEqual(b"\xff", buff)

        reg = Register(name="REG1", address=1, size=2, access_type=R, value=-2, is_signed=True)
        buff = reg.encode()
        self.assertEqual(b"\xfe\xff", buff)

        reg = Register(name="REG1", address=1, size=4, access_type=R, value=-3, is_signed=True)
        buff = reg.encode()
        self.assertEqual(b"\xfd\xff\xff\xff", buff)

    def test_decode(self):
        reg = Register(name="REG1", address=1, size=1, access_type=R, value=0)
        reg.decode(b"\x01")
        self.assertEqual(1, reg.value)

        reg = Register(name="REG1", address=1, size=2, access_type=R, value=0)
        reg.decode(b"\x01\x02")
        self.assertEqual(0x0201, reg.value)

        reg = Register(name="REG1", address=1, size=4, access_type=R, value=0)
        reg.decode(b"\x01\x02\x03\x04")
        self.assertEqual(0x04030201, reg.value)

        reg = Register(name="REG1", address=1, size=1, access_type=R, value=0, is_signed=True)
        reg.decode(b"\xff")
        self.assertEqual(-1, reg.value)

        reg = Register(name="REG1", address=1, size=2, access_type=R, value=0, is_signed=True)
        reg.decode(b"\xfe\xff")
        self.assertEqual(-2, reg.value)

        reg = Register(name="REG1", address=1, size=4, access_type=R, value=0, is_signed=True)
        reg.decode(b"\xfd\xff\xff\xff")
        self.assertEqual(-3, reg.value)


if __name__ == '__main__':
    unittest.main()
