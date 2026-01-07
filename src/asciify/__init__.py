"""A CLI program and library that turns images into colorized ASCII art."""

from typing import List

from .core import asciify
from .process import ImgProcessor
from .renderer import Renderer
from .utils import DEFAULT_CHARSET

__version__ = "1.0.2"

__all__: List[str] = ["asciify", "ImgProcessor", "Renderer", "DEFAULT_CHARSET"]
