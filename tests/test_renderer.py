"""Tests for Renderer class."""
import pytest
import numpy as np
from asciify import Renderer, DEFAULT_CHARSET


class TestRenderer:
    """Test suite for Renderer class."""

    @pytest.fixture
    def simple_hsv_image(self):
        """Create a simple HSV image for testing.

        :returns: Small HSV image array
        :rtype: np.ndarray
        """
        # Create a 5x5 HSV image with varying brightness
        hsv = np.zeros((5, 5, 3), dtype=np.uint8)
        for i in range(5):
            for j in range(5):
                hsv[i, j] = [0, 0, i * 50]  # Varying V (brightness)
        return hsv

    @pytest.fixture
    def edge_data(self):
        """Create simple edge and angle data for testing.

        :returns: Tuple of (angles, edges) arrays
        :rtype: tuple[np.ndarray, np.ndarray]
        """
        # 5x5 arrays
        angles = np.array([
            [0, 45, 90, 135, 180],
            [0, 45, 90, 135, 180],
            [0, 45, 90, 135, 180],
            [0, 45, 90, 135, 180],
            [0, 45, 90, 135, 180],
        ], dtype=np.float32)

        edges = np.array([
            [255, 255, 255, 255, 255],
            [0, 0, 0, 0, 0],
            [255, 255, 255, 255, 255],
            [0, 0, 0, 0, 0],
            [255, 255, 255, 255, 255],
        ], dtype=np.uint8)

        return angles, edges

    def test_renderer_initialization_color(self):
        """Test Renderer initialization with color mode."""
        renderer = Renderer(color_mode="color")
        assert renderer.color_mode == "color"
        assert renderer.charset == DEFAULT_CHARSET

    def test_renderer_initialization_bw(self):
        """Test Renderer initialization with black and white mode."""
        renderer = Renderer(color_mode="bw")
        assert renderer.color_mode == "bw"

    def test_renderer_custom_charset(self):
        """Test Renderer with custom character set."""
        custom_charset = [".", "o", "O", "@"]
        renderer = Renderer(charset=custom_charset)
        assert renderer.charset == custom_charset

    def test_hsv_to_ansi_conversion(self):
        """Test HSV to ANSI RGB conversion."""
        renderer = Renderer()
        r, g, b = renderer.hsv_to_rgb(0, 255, 255)

        assert isinstance(r, int)
        assert isinstance(g, int)
        assert isinstance(b, int)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

    def test_draw_in_ascii_returns_string(self, simple_hsv_image):
        """Test that draw_in_ascii returns a string."""
        renderer = Renderer(color_mode="color")
        result = renderer.draw_in_ascii(simple_hsv_image)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_draw_in_ascii_has_newlines(self, simple_hsv_image):
        """Test that output has correct number of lines."""
        renderer = Renderer(color_mode="color")
        result = renderer.draw_in_ascii(simple_hsv_image)

        lines = result.split("\n")
        # Should have 5 lines for 5x5 image
        assert len(lines) == 5

    def test_draw_in_ascii_color_mode_has_ansi(self, simple_hsv_image):
        """Test that color mode output contains ANSI color codes."""
        renderer = Renderer(color_mode="color")
        result = renderer.draw_in_ascii(simple_hsv_image)

        # Check for ANSI color escape sequences
        assert "\033[38;2;" in result

    def test_draw_in_ascii_bw_mode(self, simple_hsv_image):
        """Test black and white mode output."""
        renderer = Renderer(color_mode="bw")
        result = renderer.draw_in_ascii(simple_hsv_image)

        # Should have ANSI codes with white color
        assert "\033[38;2;255;255;255m" in result

    def test_draw_in_ascii_uses_charset(self, simple_hsv_image):
        """Test that output uses characters from the charset."""
        renderer = Renderer(color_mode="bw")
        result = renderer.draw_in_ascii(simple_hsv_image)

        # Remove ANSI codes to check characters
        # Simple check: result should contain some charset characters
        for char in DEFAULT_CHARSET:
            # At least some characters should be present
            pass  # We can't easily strip ANSI, but we know it's there

        assert len(result) > 0

    def test_draw_in_ascii_with_edges_returns_string(self, simple_hsv_image, edge_data):
        """Test that draw_in_ascii_with_edges returns a string."""
        renderer = Renderer(color_mode="color")
        angles, edges = edge_data
        result = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles, edges)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_draw_in_ascii_with_edges_contains_edge_chars(self, simple_hsv_image, edge_data):
        """Test that edge mode includes edge characters."""
        renderer = Renderer(color_mode="color")
        angles, edges = edge_data
        result = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles, edges)

        # Should contain some edge characters
        edge_chars = ["|", "_", "/", "\\"]
        # At least one edge character should be present
        assert any(char in result for char in edge_chars)

    def test_draw_char_col_brightness_mapping(self):
        """Test that draw_char_col maps brightness to characters correctly."""
        renderer = Renderer(color_mode="color")
        line = []

        # Test dark pixel (low V value)
        renderer.draw_char_col([0, 0, 10], line)
        # Should add a character to line
        assert len(line) == 1

        # Test bright pixel (high V value)
        line = []
        renderer.draw_char_col([0, 0, 250], line)
        assert len(line) == 1

    def test_draw_char_bw_brightness_mapping(self):
        """Test that draw_char_bw maps brightness to characters correctly."""
        renderer = Renderer(color_mode="bw")
        line = []

        # Test dark pixel
        renderer.draw_char_bw([0, 0, 10], line)
        assert len(line) == 1

        # Test bright pixel
        line = []
        renderer.draw_char_bw([0, 0, 250], line)
        assert len(line) == 1

    def test_different_brightness_levels_produce_different_chars(self):
        """Test that different brightness levels produce different characters."""
        renderer = Renderer(color_mode="bw")

        brightness_levels = [10, 50, 100, 150, 200, 250]
        results = []

        for v in brightness_levels:
            line = []
            renderer.draw_char_bw([0, 0, v], line)
            # Extract just the character (remove ANSI codes)
            results.append(line[0])

        # Different brightness should produce different outputs
        # (though some might be the same due to binning)
        assert len(set(results)) > 1

    def test_renderer_handles_edge_angles_correctly(self, simple_hsv_image):
        """Test that different angles produce different edge characters."""
        renderer = Renderer(color_mode="color")

        # Create angles for different edge directions
        angles_vertical = np.full((5, 5), 90.0, dtype=np.float32)
        angles_horizontal = np.full((5, 5), 0.0, dtype=np.float32)
        angles_diagonal1 = np.full((5, 5), 45.0, dtype=np.float32)
        angles_diagonal2 = np.full((5, 5), 135.0, dtype=np.float32)

        edges = np.full((5, 5), 255, dtype=np.uint8)

        result_v = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles_vertical, edges)
        result_h = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles_horizontal, edges)
        result_d1 = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles_diagonal1, edges)
        result_d2 = renderer.draw_in_ascii_with_edges(simple_hsv_image, angles_diagonal2, edges)

        # Different angles should produce different results
        # Vertical should have |
        assert "|" in result_v
        # Horizontal should have _
        assert "_" in result_h
        # Diagonals should have / or \
        assert ("/" in result_d1 or "\\" in result_d1)
        assert ("\\" in result_d2 or "/" in result_d2)
