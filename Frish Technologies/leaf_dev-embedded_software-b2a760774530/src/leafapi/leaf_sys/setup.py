import os
from distutils.core import setup, Extension


LEAF_FIRMWARE_PATH = '../../../leaf_firmware'


def lf_path(p: str) -> str:
    return os.path.abspath(os.path.join(LEAF_FIRMWARE_PATH, p))


name = "serial_protocol"
version = "1.0"
ext_modules = Extension(name="_serial_protocol",
                        sources=["serial_protocol.i",
                                 lf_path("common/serial_protocol/serial_protocol.c")],
                        include_dirs=['.', lf_path('common'), lf_path('common/serial_protocol')],
                        swig_opts=['-I.', '-I' + lf_path('common'), '-I' + lf_path('common/serial_protocol')])
setup(name=name, version=version, ext_modules=[ext_modules])

name = "mb_data"
version = "1.0"
ext_modules = Extension(name="_mb_data",
                        sources=["mb_data.i"],
                        # define_macros=[('SWIG',)],
                        include_dirs=['.', lf_path(''), lf_path('common')],
                        swig_opts=['-I.', '-I' + lf_path('common')])
setup(name=name, version=version, ext_modules=[ext_modules])

name = "climat_board"
version = "1.0"
ext_modules = Extension(name="_climat_board",
                        sources=["climat_board.i"],
                        # define_macros=[('SWIG',)],
                        include_dirs=['.', lf_path(''), lf_path('common')],
                        swig_opts=['-I.', '-I' + lf_path('common')])
setup(name=name, version=version, ext_modules=[ext_modules])
