"""Pytest configuration and shared fixtures."""
import pytest
import numpy as np
import cv2
from pathlib import Path


@pytest.fixture
def test_image_path(tmp_path):
    """Create a small test image and return its path.

    :param tmp_path: pytest's temporary directory fixture
    :returns: Path to the created test image
    :rtype: Path
    """
    # Create a simple 100x100 test image with a gradient
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    # Create a gradient pattern
    for i in range(100):
        for j in range(100):
            img[i, j] = [i * 2, j * 2, (i + j) % 255]

    # Add a white square in the center (for edge detection testing)
    img[40:60, 40:60] = [255, 255, 255]

    # Save the image
    image_path = tmp_path / "test_image.png"
    cv2.imwrite(str(image_path), img)

    return image_path


@pytest.fixture
def small_test_image_path(tmp_path):
    """Create a very small test image for quick tests.

    :param tmp_path: pytest's temporary directory fixture
    :returns: Path to the created test image
    :rtype: Path
    """
    # Create a tiny 10x10 image
    img = np.array([
        [[0, 0, 0], [50, 50, 50], [100, 100, 100], [150, 150, 150], [200, 200, 200],
         [255, 255, 255], [200, 200, 200], [150, 150, 150], [100, 100, 100], [50, 50, 50]],
    ] * 10, dtype=np.uint8)

    image_path = tmp_path / "small_test.png"
    cv2.imwrite(str(image_path), img)

    return image_path
