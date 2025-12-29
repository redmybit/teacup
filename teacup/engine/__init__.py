"""
Teacup Engine

Resources used by teacup internally
"""

from .core import ScreenObject, Rectangle, Ellipse, Text, Window, init, done, register_window, RUNNING, sleep, display
from . import draw # disambiguate between Rectangle and RECT
from . import font
from . import style
