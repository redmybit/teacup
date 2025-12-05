import sys
import os
import pickle
import base64
import warnings
import subprocess
from importlib.resources import files

# used by _window_process.py
def _translate_window_data(binary : bytes) -> dict:
    """
    Internal function used for transforming binary windows data back into windows data
    """

    b64 = base64.b64decode(binary.encode("ascii")) # convert to binary
    return pickle.loads(b64) # convert to dict

def get_default_window_data() -> dict:
    """
    Returns a dict of default values for window data. Automatically assigned when creating
    a window, should mainly be used for reference.
    """

    return {
        "title": "Teacup Window",
        "icon": files("teacup.assets") / "icon.png",
        "size": (500, 500)
    }

def is_valid_window_data(data : dict) -> bool:
    """
    Returns True/False if a dict contains valid window init data.
    Used to prevent errors internally.
    """

    # preliminary check
    if not type(data) is dict: return False

    checklist = [
        ("title", str),
        ("icon", object), # path-like, object is placeholder
        ("size", tuple)
    ] # keyname, expected type(s) in tuple

    # secondary check
    for check in checklist:
        if not check[0] in data: return False # in dict
        if not isinstance(data[check[0]], check[1]): return False # matches type
    
    # specific checks
    if not (len(data["size"]) == 2 and all(isinstance(axis, int) for axis in data["size"])):
        return False # window size must be tuple[int, int] with len 2
    
    try: # check if icon is a path
        os.fspath(data["icon"])
    except TypeError:
        return False

    return True

class Window:
    def __init__(self, window_data : dict = get_default_window_data()) -> None:
        """
        Window Class used for quickly creating a window
        """

        if is_valid_window_data(window_data):
            self.window_data = window_data # window data
        else:
            print(window_data)
            raise Exception("Invalid window data")

        self._process = None # from subprocess.Popen
        self._binary_data = None # binary data passed when using subprocess

        # build the window
        self.build()

    def build(self) -> None:
        """
        (re)build the window's internal data
        """
        binary = pickle.dumps(self.window_data) # convert to binary
        self._binary_data = base64.b64encode(binary).decode("ascii") # convert to UTF-8 using B64

    def kill(self) -> None:
        """
        Kills the window
        """

        if self._process is not None and self._process.poll() is None:
            self._process.terminate()

            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()

        self._process = None # clear

    def _start(self) -> None:
        """
        Internal function for starting the window
        """
        
        # safety checks
        if self._process:
            warnings.warn("Window overriding previous window")
            self.kill()
        
        if self._binary_data is None:
            warnings.warn("Window not properly built yet!")
            self.build()

        # launch as module
        self._process = subprocess.Popen([
            sys.executable,
            "-m",
            "teacup.engine._window_process",
            self._binary_data
        ])

    def _stop(self) -> None:
        """
        Internal function for closing the window
        """

        self.kill()

    def __enter__(self):
        self._start()
        return self
    
    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop()
