import argparse
from pathlib import Path

from .core import asciify


def main():
    """CLI's entry point"""
    parser = argparse.ArgumentParser(
        prog="asciify",
        description="Turn every image in colorized ASCII art",
        epilog="Thanks for using %(prog)s!",
    )

    parser.add_argument(
        "image_path", type=str, action="store", help="Provide input image's path"
    )

    parser.add_argument(
        "-bw",
        "--black_white",
        action="store_true",
        help="Set the output to black and white",
    )

    parser.add_argument(
        "-e", "--edges", action="store_true", help="Enable edge detection and printing"
    )

    parser.add_argument(
        "-w",
        "--width",
        type=int,
        action="store",
        help="Provide custom width. If not specified, terminal's size is going to determine this value. This value can be specified only when f_type='wide'",
    )

    parser.add_argument(
        "-he",
        "--height",
        type=int,
        action="store",
        help="Provide custom height. If not specified, terminal's size is going to determine this value. This value can be specified only when f_type='in_terminal' or 'tall'",
    )

    parser.add_argument(
        "-ar",
        "--no_aspect_ratio",
        action="store_false",
        help="Disable original aspect ratio's protection",
    )

    parser.add_argument(
        "-f",
        "--factor_type",
        type=str,
        choices=["in_terminal", "wide", "tall"],
        action="store",
        help="Choose the downsampling factor type among the following values: %(choices)s",
    )

    parser.add_argument(
        "-b",
        "--blur",
        type=list,
        action="store",
        help="Provide a list with kernel size as a tuple, std for x axis, std for y axis. For more details refer to the docs for `cv2.GaussianBlur`",
    )

    parser.add_argument(
        "-ct",
        "--canny_threshold",
        type=tuple,
        action="store",
        help="Provide edges detection threshold as a tuple. For more details refer to the docs for `cv2.Canny`",
    )

    parser.add_argument(
        "-at",
        "--angles_threshold",
        type=int,
        action="store",
        help="Provide kernel size for angles calculation as an integer",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        action="store",
        help="Provide the output's path. If not specified, uses stdout",
    )

    args = parser.parse_args()

    target_image = Path(args.image_path)

    if not target_image.exists():
        print(f"Impossible to find {target_image}")
        raise SystemExit(1)

    kwargs = {
        "image_path": args.image_path,
        "color_mode": "bw" if args.black_white else "color",
        "edges_detection": args.edges,
        "f_type": "in_terminal" if not args.factor_type else args.factor_type,
        "keep_aspect_ratio": args.no_aspect_ratio,
    }

    if args.width is not None:
        kwargs["width"] = args.width

    if args.height is not None:
        kwargs["height"] = args.height

    if args.blur is not None:
        kwargs["blur"] = args.blur

    if args.canny_threshold is not None:
        kwargs["canny_threshold"] = args.canny_threshold

    if args.angles_threshold is not None:
        kwargs["angles_threshold"] = args.angles_threshold

    result = asciify(**kwargs)

    if args.output is None:
        print(result)

    else:
        with open(args.output, "w") as f:
            f.write(result)
