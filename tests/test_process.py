"""Tests for ImgProcessor class."""
import pytest
import numpy as np
from asciify import ImgProcessor


class TestImgProcessor:
    """Test suite for ImgProcessor class."""

    def test_load_image(self, test_image_path):
        """Test that image is loaded correctly."""
        processor = ImgProcessor(str(test_image_path))
        assert processor.image is not None
        assert isinstance(processor.image, np.ndarray)
        assert len(processor.image.shape) == 3  # Height, Width, Channels

    def test_load_nonexistent_image(self):
        """Test loading non-existent image returns None."""
        processor = ImgProcessor("/nonexistent/image.jpg")
        # cv2.imread returns None for non-existent files
        assert processor.image is None

    def test_calculate_downsample_factor_with_aspect_ratio(self, test_image_path):
        """Test downsample factor calculation with aspect ratio."""
        processor = ImgProcessor(str(test_image_path))
        factor = processor.calculate_downsample_factor(
            term_height=50,
            term_width=100,
            keep_aspect_ratio=True,
            f_type="in_terminal"
        )
        assert isinstance(factor, int)
        assert factor > 0

    def test_calculate_downsample_factor_without_aspect_ratio(self, test_image_path):
        """Test downsample factor calculation without aspect ratio."""
        processor = ImgProcessor(str(test_image_path))
        factors = processor.calculate_downsample_factor(
            term_height=50,
            term_width=100,
            keep_aspect_ratio=False
        )
        assert isinstance(factors, tuple)
        assert len(factors) == 2
        assert all(isinstance(f, int) for f in factors)
        assert all(f > 0 for f in factors)

    def test_calculate_downsample_factor_types(self, test_image_path):
        """Test different downsample factor types."""
        processor = ImgProcessor(str(test_image_path))

        for f_type in ["in_terminal", "tall", "wide"]:
            factor = processor.calculate_downsample_factor(
                term_height=50,
                term_width=100,
                keep_aspect_ratio=True,
                f_type=f_type
            )
            assert isinstance(factor, int)
            assert factor > 0

    def test_downsample_image(self, test_image_path):
        """Test image downsampling."""
        processor = ImgProcessor(str(test_image_path))
        original_shape = processor.image.shape

        downsampled = processor.downsample_image(f=2, keep_aspect_ratio=True)

        assert isinstance(downsampled, np.ndarray)
        assert len(downsampled.shape) == 3
        # Downsampled image should be smaller
        assert downsampled.shape[0] < original_shape[0]
        assert downsampled.shape[1] < original_shape[1]

    def test_convert_to_hsv(self, test_image_path):
        """Test BGR to HSV conversion."""
        processor = ImgProcessor(str(test_image_path))
        hsv = processor.convert_to_hsv(processor.image)

        assert isinstance(hsv, np.ndarray)
        assert len(hsv.shape) == 3
        assert hsv.shape == processor.image.shape
        # HSV values should be in expected ranges
        assert hsv[:, :, 0].max() <= 180  # Hue max in OpenCV

    def test_calculate_angles(self, test_image_path):
        """Test Sobel angle calculation."""
        processor = ImgProcessor(str(test_image_path))
        angles = processor.calculate_angles(image=processor.image, k_size=3)

        assert isinstance(angles, np.ndarray)
        assert len(angles.shape) == 2  # 2D array
        # Angles should be in degrees [0, 360)
        assert angles.min() >= 0
        assert angles.max() <= 360

    def test_calculate_angles_different_kernel_sizes(self, test_image_path):
        """Test angle calculation with different kernel sizes."""
        processor = ImgProcessor(str(test_image_path))

        for k_size in [3, 5, 7]:
            angles = processor.calculate_angles(image=processor.image, k_size=k_size)
            assert isinstance(angles, np.ndarray)
            assert len(angles.shape) == 2

    def test_detect_edges(self, test_image_path):
        """Test Canny edge detection."""
        processor = ImgProcessor(str(test_image_path))
        edges = processor.detect_edges(
            image=processor.image,
            blur=[(9, 9), 1.5, 1.5],
            canny_thresh=(200, 300)
        )

        assert isinstance(edges, np.ndarray)
        assert len(edges.shape) == 2  # 2D array
        # Canny returns binary edges (0 or 255)
        assert set(np.unique(edges)).issubset({0, 255})

    def test_detect_edges_with_different_thresholds(self, test_image_path):
        """Test edge detection with different Canny thresholds."""
        processor = ImgProcessor(str(test_image_path))

        edges_low = processor.detect_edges(
            image=processor.image,
            canny_thresh=(50, 100)
        )
        edges_high = processor.detect_edges(
            image=processor.image,
            canny_thresh=(200, 300)
        )

        # Lower threshold should detect more edges
        assert np.sum(edges_low > 0) >= np.sum(edges_high > 0)

    def test_detect_edges_with_custom_blur(self, test_image_path):
        """Test edge detection with custom blur parameters."""
        processor = ImgProcessor(str(test_image_path))
        edges = processor.detect_edges(
            image=processor.image,
            blur=[(5, 5), 1.0, 1.0],
            canny_thresh=(100, 200)
        )

        assert isinstance(edges, np.ndarray)
        assert set(np.unique(edges)).issubset({0, 255})

    def test_pipeline_integration(self, test_image_path):
        """Test full processing pipeline."""
        processor = ImgProcessor(str(test_image_path))

        # Downsample
        factor = processor.calculate_downsample_factor(50, 100)
        ds_img = processor.downsample_image(f=factor)

        # Convert to HSV
        hsv = processor.convert_to_hsv(ds_img)

        # Calculate angles and edges
        angles = processor.calculate_angles(image=ds_img)
        edges = processor.detect_edges(image=ds_img)

        # All should have compatible shapes
        assert hsv.shape[:2] == angles.shape
        assert hsv.shape[:2] == edges.shape
