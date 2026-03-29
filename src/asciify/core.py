from typing import Optional, Union

import numpy as np

from .process import ImgProcessor
from .renderer import Renderer
from .utils import DEFAULT_CHARSET


def asciify(
    image_path: str,
    color_mode: str = "color",
    edges_detection: bool = False,
    width: Optional[int] = None,
    height: Optional[int] = None,
    keep_aspect_ratio: bool = True,
    f_type: str = "in_terminal",
    blur: list[tuple[int, int], float, float] = [(9, 9), 1.5, 1.5],
    canny_thresh: tuple[int, int] = (200, 300),
    angles_thresh: int = 3,
    aspect_ratio_correction: float = 1.10,
    charset: list[str] = DEFAULT_CHARSET,
    output_format: str = "text",
) -> Union[str, np.ndarray]:
    """
    Draw the input image in ASCII art. This function wraps the objects defined in ``process.py`` and ``renderer.py`` and orchestrate their workflow.

    Refer to the docs for :class:`ImgProcessor` and :class:`Renderer` for further details.

    :param output_format: Output format, either "text" (returns ANSI-colored string) or "png" (returns RGB numpy array).
    :type output_format: str
    :return: Either a string (text mode) or a numpy array of shape (height, width, 3) (PNG mode).
    :rtype: Union[str, np.ndarray]
    """

    processor = ImgProcessor(image_path)

    if output_format == "png":
        m, n, _ = processor.image.shape
        if height is None and width is not None:
            height = round(width * (m / n))
        elif width is None and height is not None:
            width = round(height * (n / m))
        elif height is None and width is None:
            term_height, term_width = processor.calculate_print_size()
            height = round(term_width * (m / n))
            width = term_width
        term_height, term_width = height, width

        ds_f = processor.calculate_downsample_factor(
            term_height=term_height,
            term_width=term_width,
            keep_aspect_ratio=False,
            f_type="pixel",
            aspect_ratio_correction=aspect_ratio_correction,
        )
        ds_img = processor.downsample_image(
            f=ds_f,
            keep_aspect_ratio=False,
        )
    else:
        if not height and not width:
            term_height, term_width = processor.calculate_print_size()
        else:
            term_height, term_width = height, width

        ds_f = processor.calculate_downsample_factor(
            term_height=term_height,
            term_width=term_width,
            keep_aspect_ratio=keep_aspect_ratio,
            f_type=f_type,
            aspect_ratio_correction=aspect_ratio_correction,
        )
        ds_img = processor.downsample_image(
            f=ds_f,
            aspect_ratio_correction=aspect_ratio_correction,
            keep_aspect_ratio=keep_aspect_ratio,
        )
    img_hsv = processor.convert_to_hsv(image=ds_img)
    angles = processor.calculate_angles(image=ds_img, k_size=angles_thresh)
    edges = processor.detect_edges(image=ds_img, blur=blur, canny_thresh=canny_thresh)

    renderer = Renderer(color_mode=color_mode, charset=charset)

    if edges_detection:
        return renderer.draw_in_ascii_with_edges(
            img_hsv=img_hsv, angles=angles, edges=edges
        )

    if output_format == "png":
        return renderer.draw_in_pixels(img_hsv=img_hsv)

    return renderer.draw_in_ascii(img_hsv=img_hsv)
