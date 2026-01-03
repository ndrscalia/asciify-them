import colorsys

DEFAULT_CHARSET = [" ", ".", "-", "=", "+", "*", "x", "#", "$", "&", "X", "@"]


def hsv_to_ansi(h, s, v):
    """Convert HSV (OpenCV: h: 0-360, s: 0-100, v: 0-100) to ANSI escape code"""
    # s = min(255, int(s * 1.5))
    # v = min(255, int(v * 1.5))

    r, g, b = colorsys.hsv_to_rgb(h / 179, s / 255, v / 255)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b
