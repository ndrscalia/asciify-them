import colorsys

import numpy as np

from .utils import DEFAULT_CHARSET


class Renderer:
    """
    Draw ASCII art from the results obtained with :class:`ImgProcessor`.
    """

    def __init__(self, color_mode="color", charset=None):
        self.color_mode = color_mode
        self.charset = charset or DEFAULT_CHARSET
        self.drawing_function = {"color": self.draw_char_col, "bw": self.draw_char_bw}

    def hsv_to_rgb(self, h: int, s: int, v: int):
        """
        Convert HSV (OpenCV: h: 0-360, s: 0-100, v: 0-100) to RGB.

        :param h: Hue value from pixel.
        :type h: int
        :param s: Saturation value from pixel.
        :type s: int
        :param v: Value from pixel.
        :type v: int
        :return: A tuple containing the equivalent RGB value.
        :rtype: tuple[int, int, int]
        """
        # s = min(255, int(s * 1.5))
        # v = min(255, int(v * 1.5))

        r, g, b = colorsys.hsv_to_rgb(h / 179, s / 255, v / 255)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return r, g, b

    def draw_char_col(self, pixel: np.ndarray, line: list):
        """
        Draw ASCII image chosing the right char based on the pixel's value (HSV), while coloring it with ansi escape codes based on the equivalent RGB.

        :param pixel: HSV pixel.
        :type pixel: np.ndarray
        :param line: A list containing the string for the pixels of every line.
        :type line: list
        """
        h, s, v = pixel
        r, g, b = self.hsv_to_rgb(h, s, v)
        if v <= 42:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[0]}")
        elif v <= 61:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[1]}")
        elif v <= 80:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[2]}")
        elif v <= 99:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[3]}")
        elif v <= 118:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[4]}")
        elif v <= 137:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[5]}")
        elif v <= 156:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[6]}")
        elif v <= 175:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[7]}")
        elif v <= 194:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[8]}")
        elif v <= 213:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[9]}")
        elif v <= 232:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[10]}")
        elif v <= 255:
            line.append(f"\033[38;2;{r};{g};{b}m{self.charset[11]}")

    def draw_char_bw(self, pixel: np.ndarray, line: list):
        """
        Draw ASCII image chosing the right char based on the pixel's value (HSV) and coloring every char in white.

        :param pixel: HSV pixel.
        :type pixel: np.ndarray
        :param line: A list containing the string for the pixels of every line.
        :type line: list
        """
        h, s, v = pixel
        r, g, b = self.hsv_to_rgb(h, s, v)
        if v <= 42:
            line.append(f"\033[38;2;255;255;255m{self.charset[0]}")
        elif v <= 61:
            line.append(f"\033[38;2;255;255;255m{self.charset[1]}")
        elif v <= 80:
            line.append(f"\033[38;2;255;255;255m{self.charset[2]}")
        elif v <= 99:
            line.append(f"\033[38;2;255;255;255m{self.charset[3]}")
        elif v <= 118:
            line.append(f"\033[38;2;255;255;255m{self.charset[4]}")
        elif v <= 137:
            line.append(f"\033[38;2;255;255;255m{self.charset[5]}")
        elif v <= 156:
            line.append(f"\033[38;2;255;255;255m{self.charset[6]}")
        elif v <= 175:
            line.append(f"\033[38;2;255;255;255m{self.charset[7]}")
        elif v <= 194:
            line.append(f"\033[38;2;255;255;255m{self.charset[8]}")
        elif v <= 213:
            line.append(f"\033[38;2;255;255;255m{self.charset[9]}")
        elif v <= 232:
            line.append(f"\033[38;2;255;255;255m{self.charset[10]}")
        elif v <= 255:
            line.append(f"\033[38;2;255;255;255m{self.charset[11]}")

    def draw_in_ascii(self, img_hsv: np.ndarray):
        """
        Draw the image with the corresponding drawing function.

        :param img_hsv: The downsampled image in HSV format.
        :type img_hsv: np.ndarray
        :param angles: The angles extracted from the downsampled image.
        :return: Strings composing the ASCII image, with returns for every line.
        :rtype: str
        """

        lines = []

        for row_im in img_hsv:
            line = []
            for pixel_im in row_im:
                self.drawing_function[self.color_mode](pixel_im, line)

            lines.append(line)

        return "\n".join("".join(line) for line in lines)

    def draw_in_ascii_with_edges(
        self, img_hsv: np.ndarray, angles: np.ndarray, edges: np.ndarray
    ):
        """
        Draw edges according to angles and draw them with the corresponding drawing function.

        :param img_hsv: The downsampled image in HSV format.
        :type img_hsv: np.ndarray
        :param angles: The angles extracted from the downsampled image.
        :type img_hsv: np.ndarray
        :param edges: The edges extracted from the downsampled image.
        :type edges: np.ndarray
        :return: Strings composing the ASCII image, with returns for every line.
        :rtype: str
        """

        lines = []

        for row_im, row_ang, row_edg in zip(img_hsv, angles, edges):
            line = []
            for pixel_im, pixel_ang, pixel_edg in zip(row_im, row_ang, row_edg):
                if pixel_edg > 0:
                    if 80 <= pixel_ang < 100 or 260 <= pixel_ang < 280:
                        line.append("\033[38;2;255;255;255m|")
                    elif (
                        170 <= pixel_ang < 190
                        or 350 <= pixel_ang < 360
                        or 0 <= pixel_ang < 10
                    ):
                        line.append("\033[38;2;255;255;255m_")
                    elif 35 <= pixel_ang < 55 or 215 <= pixel_ang < 235:
                        line.append("\033[38;2;255;255;255m/")
                    elif 125 <= pixel_ang < 145 or 305 <= pixel_ang < 325:
                        line.append("\033[38;2;255;255;255m\\")
                    else:
                        self.drawing_function[self.color_mode](pixel_im, line)
                else:
                    self.drawing_function[self.color_mode](pixel_im, line)

            lines.append(line)

        return "\n".join("".join(line) for line in lines)
