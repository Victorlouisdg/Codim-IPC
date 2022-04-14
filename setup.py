import os
import subprocess

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

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

        print("PYTHON IS ", BLENDER_PYTHON)
        print("PYTHON_INCLUDE IS", PYTHON_INCLUDE)
        print("PYTHON_LIBS IS", PYTHON_LIBS)

        # os.makedirs(extdir)

        runCommand = f"mkdir build\ncd build\nrm -rf CMakeCache.txt\ncmake -DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir} -DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir} -DCMAKE_BUILD_TYPE=Release -DPYTHON_EXECUTABLE:FILEPATH={BLENDER_PYTHON} -DPYTHON_LIBRARIES={PYTHON_LIBS} -DPYTHON_INCLUDE_DIRS={PYTHON_INCLUDE} ..\nmake -j 12"
        subprocess.call([runCommand], shell=True)


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