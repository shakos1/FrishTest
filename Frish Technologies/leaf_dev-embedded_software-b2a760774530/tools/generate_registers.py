import argparse


def generate(src, dst_fp, reg_type, access_type):
    with open(src, 'r') as fp:
        name = ''
        size = ''
        for line in fp.readlines():

            if line.startswith(reg_type):
                n = line.split(' ')[0]
                if name == '':
                    name = n[len(reg_type):]
                    address = n

                if n.endswith('_SIZE'):
                    size = n

            if name and size:
                dst_fp.write(
                    f"    {name} = Register(name='{name}', address={address}, size={size} * 2, access_type={access_type})\n")

                name = ''
                size = ''


def generate_registers_class(src: str, dst: str):
    dst_fp = open(dst, 'w')

    dst_fp.write("from registers.register import Register, R, W, RW\n")
    dst_fp.write("from leafapi.leaf_sys.mb_data import *\n")
    dst_fp.write("\n\n")
    dst_fp.write("class InputRegisters:\n")

    reg_type = 'MB_IR_'
    access_type = 'R'
    generate(src, dst_fp, reg_type, access_type)

    dst_fp.write("\n\n")
    dst_fp.write("class HoldingRegisters:\n")

    reg_type = 'MB_HR_'
    access_type = 'RW'
    generate(src, dst_fp, reg_type, access_type)

    dst_fp.close()


if __name__ == '__main__':
    default_src = '../src/leafapi/leaf_sys/mb_data.py'
    default_dst = '../src/registers/sys_registers.py'

    parser = argparse.ArgumentParser(description='Helper script to generate Register description file.')
    parser.add_argument('--mb_data', action='store', default=default_src,
                        help='Path to mb_data.py file.')
    parser.add_argument('--out', action='store', default=default_dst,
                        help='Path to mb_data.py file.')

    args = parser.parse_args()

    generate_registers_class(args.mb_data, args.out)
