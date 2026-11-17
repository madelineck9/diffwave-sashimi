import sys
from setuptools import setup
import torch.cuda
from torch.utils.cpp_extension import CppExtension, CUDAExtension, BuildExtension
from torch.utils.cpp_extension import CUDA_HOME

# GCC-only flags; MSVC (Windows) needs its own equivalents.
# CUDA 13's CCCL headers require MSVC's conforming preprocessor (/Zc:preprocessor), for cl.exe and nvcc's host compiler.
if sys.platform == 'win32':
    cxx_flags = ['/O2', '/Zc:preprocessor']
    nvcc_host_flags = ['-Xcompiler', '/Zc:preprocessor']
else:
    cxx_flags = ['-g', '-march=native', '-funroll-loops']
    nvcc_host_flags = []

ext_modules = []
if torch.cuda.is_available() and CUDA_HOME is not None:
    extension = CUDAExtension(
        'cauchy_mult', [
            'cauchy.cpp',
            'cauchy_cuda.cu',
        ],
        extra_compile_args={'cxx': cxx_flags,
                            # 'nvcc': ['-O2', '-lineinfo']
                            'nvcc': ['-O2', '-lineinfo', '--use_fast_math'] + nvcc_host_flags
                            }
    )
    ext_modules.append(extension)
else:
    # Without this, setup.py "succeeds" but installs an empty package and the extension is silently missing
    raise RuntimeError(
        f"Cannot build cauchy_mult: torch.cuda.is_available()={torch.cuda.is_available()}, CUDA_HOME={CUDA_HOME}. "
        "Install the CUDA Toolkit (nvcc) matching torch.version.cuda and use a CUDA build of PyTorch."
    )

setup(
    name='cauchy_mult',
    ext_modules=ext_modules,
    # cmdclass={'build_ext': BuildExtension.with_options(use_ninja=False)})
    cmdclass={'build_ext': BuildExtension})
