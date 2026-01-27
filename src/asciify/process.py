import math
import os

import cv2
import numpy as np

from .utils import get_font_aspect_ratio


class ImgProcessor:
    """
    Prepare the image for drawing with :class:`Renderer`.
    """

    def __init__(self, path_to_image: str):
        """
        On initialization, the class loads an image.

        :param path_to_image: The path to the input image.
        :type path_to_image: str
        """
        self.path_to_image = path_to_image
        self.image = self._load_image(path_to_image)

    def calculate_print_size(self):
        """
        If no custom height/width is provided, the print size is derived from the terminal's size.

        :return: Terminal's height in lines and terminal's width in columns.
        :rtype: tuple[int, int]
        """
        try:
            if os.name != "nt":
                with open("/dev/tty") as tty:
                    t_size = os.get_terminal_size(tty.fileno())
            else:
                import shutil

                t_size = shutil.get_terminal_size()

            t_height = t_size.lines
            t_width = t_size.columns
        except (OSError, IOError):
            raise RuntimeError("Impossible to get terminal size! Good luck!")

        return t_height, t_width

    def _load_image(self, path_to_image: str):
        """
        Read the original image and returns image as an array.

        :param path_to_image: Path where to find the image.
        :type path_to_image: str
        :return: A three dimensional array of pixel values.
        :rtype: np.ndarray
        """
        img = cv2.imread(path_to_image)

        return img

    def calculate_downsample_factor(
        self,
        term_height: int,
        term_width: int,
        keep_aspect_ratio=True,
        f_type="in_terminal",
        aspect_ratio_correction: float = 1.10,
    ):
        """
        Calculate downsample factor according to different needs. Refer to the README.md for the different ``f_type`` values.

        :param term_height: Terminal's height in lines.
        :type term_height: int
        :param term_width: Terminal's width in columns.
        :type term_width: int
        :param keep_aspect_ratio: Choose wether or not to preserve the original aspect ratio.
        :type keep_aspect_ratio: bool
        :param f_type: Provide the different kinds of downsampling factors available.
        :type f_type: str
        :param aspect_ratio_correction: Factor by which horizontal stretch can be limited to better estimate font aspect ratio in terminal.
        :type aspect_ratio_correction: float
        :return: Single factor if ``keep_aspect_ratio=True``, tuple of two factors if ``keep_aspect_ratio=False``
        :rtype: int or tuple[int, int]

        :raises ValueError: if ``f_type`` is not chosen among ``in_terminal``, ``tall``, and ``wide``.
        """

        m, n, _ = self.image.shape

        if keep_aspect_ratio:
            if f_type == "in_terminal":
                font_aspect_ratio = get_font_aspect_ratio() / aspect_ratio_correction
                f_height = max(1, m // term_height)
                f_width = max(1, math.ceil(n * font_aspect_ratio / term_width))

                f = max(1, f_height, f_width)

            elif f_type == "tall":
                f = max(1, m // term_width)

            elif f_type == "wide":
                f = max(1, n // term_width)

            else:
                raise ValueError(
                    "f_type must be chosen between 'in_terminal', 'tall', and 'wide'"
                )

            return f

        else:
            fh = max(1, m // (term_height - term_height // 100 * 10))
            fw = max(1, n // (term_width - term_width // 100 * 10))

            f = fh, fw

            return f

    def downsample_image(
        self, f: int, aspect_ratio_correction: float = 1.10, keep_aspect_ratio=True
    ):
        """
        Downsample the input image.

        :param f: The downsampling factor obtained with :func:`calculate_downsample_factor`.
        :type f: int or tuple[int, int]
        :param aspect_ratio_correction: Factor by which horizontal stretch can be limited to better estimate font aspect ratio in terminal.
        :type aspect_ratio_correction: float
        :param keep_aspect_ratio: Choose wether to preserve or not original aspect ratio. It must be set to the same value as it was in :func:`calculate_downsample_factor`.
        :return: The downsampled image.
        :rtype: np.ndarray
        """

        m, n, _ = self.image.shape

        if keep_aspect_ratio:
            aspect_ratio = get_font_aspect_ratio() / aspect_ratio_correction
            width_factor = max(1, int(f / aspect_ratio))
            img = np.zeros((m // f, n // width_factor, 3), dtype=np.uint8)

            for i in range(0, m, f):
                for j in range(0, n, width_factor):
                    try:
                        img[i // f][j // width_factor] = self.image[i][j]
                    except IndexError:
                        pass

            return img

        else:
            img = np.zeros((m // f[0], n // f[1], 3), dtype=np.uint8)

            for i in range(0, m, f[0]):
                for j in range(0, n, f[1]):
                    try:
                        img[i // f[0]][j // f[1]] = self.image[i][j]
                    except IndexError:
                        pass

            return img

    def convert_to_hsv(self, image):
        """
        Convert the downsampled image to HSV.

        :param image: The downsampled image obtained with :func:`downsample_image`.
        :type image: np.ndarray
        :return: The downsampled image converted to the HSV index.
        :rtype: np.ndarray
        """

        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        return img_hsv

    def calculate_angles(self, image, k_size=3):
        """
        Calculate angles using Sobel algorithm.

        :param image: The downsampled image.
        :type image: np.ndarray
        :return: The angle for every pixel.
        :rtype: np.ndarray
        """

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        sobelx = cv2.Sobel(image_gray, cv2.CV_64F, 1, 0, ksize=k_size)
        sobely = cv2.Sobel(image_gray, cv2.CV_64F, 0, 1, ksize=k_size)

        angles = cv2.phase(sobelx, sobely, angleInDegrees=True)

        return angles

    def detect_edges(self, image, blur=[(9, 9), 1.5, 1.5], canny_thresh=(200, 300)):
        """
        Detect edges with Canny edges detection algorithm after blurring the image for improved detection.

        :param blur: Determine the blur's intensity. For more details refer to the docs for ``cv2.GaussianBlur()``.
        :type blur: list[tuple[int, int], float, float]
        :param canny_thresh: Determine the threshold for edges detection. For more details see ``cv2.Canny()``.
        :type canny_thresh: tuple[int, int]
        :return:
        :rtype:
        """

        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(
            src=image_gray, ksize=blur[0], sigmaX=blur[1], sigmaY=blur[2]
        )
        edges = cv2.Canny(
            img_blur, threshold1=canny_thresh[0], threshold2=canny_thresh[1]
        )

        return edges
