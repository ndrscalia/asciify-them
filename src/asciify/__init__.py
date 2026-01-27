"""A CLI program and library that turns images into colorized ASCII art."""

from typing import List

from .core import asciify
from .process import ImgProcessor
from .renderer import Renderer
from .utils import (
    BRAILLE_CHARSET,
    CLASSIC_GRADIENT,
    DEFAULT_CHARSET,
    EXTENDED_SMOOTH_GRADIENT,
    UNICODE_BLOCKS,
)

__version__ = "1.1.0"

__all__: List[str] = [
    "asciify",
    "ImgProcessor",
    "Renderer",
    "DEFAULT_CHARSET",
    "CLASSIC_GRADIENT",
    "EXTENDED_SMOOTH_GRADIENT",
    "UNICODE_BLOCKS",
    "BRAILLE_CHARSET",
]
