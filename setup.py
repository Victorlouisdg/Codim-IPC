import os
import re
import subprocess
import sys

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

# Convert distutils Windows platform specifiers to CMake -A arguments
# PLAT_TO_CMAKE = {
#     "win32": "Win32",
#     "win-amd64": "x64",
#     "win-arm32": "ARM",
#     "win-arm64": "ARM64",
# }


# A CMakeExtension needs a sourcedir instead of a file list.
# The name must be the _single_ output extension from the CMake build.
# If you need multiple extensions, see scikit-build.
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        print("CMakeExtension(Extension)")
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def build_extension(self, ext):

        print("CMakeBuild(build_ext)")

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))


        # required for auto-detection & inclusion of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        print("extdir", extdir)


        BLENDER_MAJOR = "3.1"
        BLENDER_VERSION = "3.1.2"
        BLENDER_PYTHON_VERSION = "3.10"
        BLENDER_NAME = f"blender-{BLENDER_VERSION}-linux-x64"

        BLENDER_DIR = os.path.join(os.path.expanduser("~"), f"Blender/{BLENDER_NAME}")
        BLENDER_PYTHON_BIN_DIR = f"{BLENDER_DIR}/{BLENDER_MAJOR}/python/bin"
        BLENDER_PYTHON = f"{BLENDER_PYTHON_BIN_DIR}/python{BLENDER_PYTHON_VERSION}"

        # TODO maybe try to downlaod these into Blender python location?
        PYTHON_LIBS = f"/usr/lib/libpython{BLENDER_PYTHON_VERSION}.so"
        PYTHON_INCLUDE = f"/usr/include/python{BLENDER_PYTHON_VERSION}/"

        print("PYTHON_INCLUDE IS", PYTHON_INCLUDE)

        # os.makedirs(extdir)

        runCommand = f"mkdir build\ncd build\nrm -rf CMakeCache.txt\ncmake -DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir} -DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir} -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE:FILEPATH={BLENDER_PYTHON} -DPYTHON_LIBRARIES={PYTHON_LIBS} -DPYTHON_INCLUDE_DIRS={PYTHON_INCLUDE} ..\nmake -j 12"
        subprocess.call([runCommand], shell=True)

        # os.chdir(extdir)
        #subprocess.call(["mkdir build && rm -rf build/CMakeCache.txt"], shell=True)
        # subprocess.call([f"""cmake -DCMAKE_BUILD_TYPE=Release 
        # -DPYTHON_EXECUTABLE:FILEPATH={BLENDER_PYTHON}
        # -DPYTHON_LIBRARIES={PYTHON_LIBS}
        # -DPYTHON_INCLUDE_DIRS={PYTHON_INCLUDE}
        # ..
        # """], shell=True)
        #subprocess.call([f"cmake -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE:FILEPATH={BLENDER_PYTHON} -DPYTHON_LIBRARIES={PYTHON_LIBS} -DPYTHON_INCLUDE_DIRS={PYTHON_INCLUDE} ."], shell=True)
        # subprocess.call(["make -j 12"], shell=True)

        # debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        # cfg = "Debug" if debug else "Release"

        # # CMake lets you override the generator - we need to check this.
        # # Can be set with Conda-Build, for example.
        # cmake_generator = os.environ.get("CMAKE_GENERATOR", "")

        # # Set Python_EXECUTABLE instead if you use PYBIND11_FINDPYTHON
        # # EXAMPLE_VERSION_INFO shows you how to pass a value into the C++ code
        # # from Python.
        # cmake_args = [
        #     f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
        #     f"-DPYTHON_EXECUTABLE={sys.executable}",
        #     f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        # ]
        # build_args = []
        # # Adding CMake arguments set as environment variable
        # # (needed e.g. to build for ARM OSx on conda-forge)
        # if "CMAKE_ARGS" in os.environ:
        #     cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        # # In this example, we pass in the version to C++. You might not need to.
        # cmake_args += [f"-DEXAMPLE_VERSION_INFO={self.distribution.get_version()}"]

        # if self.compiler.compiler_type != "msvc":
        #     # Using Ninja-build since it a) is available as a wheel and b)
        #     # multithreads automatically. MSVC would require all variables be
        #     # exported for Ninja to pick it up, which is a little tricky to do.
        #     # Users can override the generator with CMAKE_GENERATOR in CMake
        #     # 3.15+.
        #     if not cmake_generator:
        #         try:
        #             import ninja  # noqa: F401

        #             cmake_args += ["-GNinja"]
        #         except ImportError:
        #             pass

        # else:

        #     # Single config generators are handled "normally"
        #     single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

        #     # CMake allows an arch-in-generator style for backward compatibility
        #     contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

        #     # Specify the arch if using MSVC generator, but only if it doesn't
        #     # contain a backward-compatibility arch spec already in the
        #     # generator name.
        #     if not single_config and not contains_arch:
        #         cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

        #     # Multi-config generators have a different way to specify configs
        #     if not single_config:
        #         cmake_args += [
        #             f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
        #         ]
        #         build_args += ["--config", cfg]

        # if sys.platform.startswith("darwin"):
        #     # Cross-compile support for macOS - respect ARCHFLAGS if set
        #     archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
        #     if archs:
        #         cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        # # Set CMAKE_BUILD_PARALLEL_LEVEL to control the parallel build level
        # # across all generators.
        # if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
        #     # self.parallel is a Python 3 only way to set parallel jobs by hand
        #     # using -j in the build_ext call, not supported by pip or PyPA-build.
        #     if hasattr(self, "parallel") and self.parallel:
        #         # CMake 3.12+ only.
        #         build_args += [f"-j{self.parallel}"]

        # build_temp = os.path.join(self.build_temp, ext.name)
        # if not os.path.exists(build_temp):
        #     os.makedirs(build_temp)

        # subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp)
        # subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=build_temp)


# The information here can also be placed in setup.cfg - better separation of
# logic and declaration, and simpler if you include description/version in a file.
setup(
    name="cipc",
    version="0.0.1",
    author="Victor-Louis De Gusseme",
    author_email="victorlouisdg@gmail.com",
    description="A Python package for C-IPC in Blender.",
    long_description="",
    ext_modules=[CMakeExtension("JGSL")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    extras_require={"test": ["pytest>=6.0"]},
    python_requires=">=3.6",
)