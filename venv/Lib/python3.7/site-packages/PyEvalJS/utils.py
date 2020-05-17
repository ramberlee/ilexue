import sys
import platform
from os import path

def get_lib_path():
    root = path.dirname(__file__)

    if sys.platform == "darwin":
        return path.join(root, "libs/osx/libChakraCore.dylib")

    if sys.platform.startswith("linux"):
        return path.join(root, "libs/linux/libChakraCore.so")

    if sys.platform == "win32":
        if platform.architecture()[0].startswith("64"):
            return path.join(root, "libs/windows/x64/ChakraCore.dll")
        else:
            return path.join(root, "libs/windows/x86/ChakraCore.dll")

    raise RuntimeError("ChakraCore not support your platform: %s, detail see: https://github.com/Microsoft/ChakraCore",
                       sys.platform)