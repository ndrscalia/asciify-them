# Tests for asciify

This directory contains the test suite for the `asciify` package.
Disclaimer: this test suite has been created with the aid of claude-code and then revised by the software's author.

## Test Structure

- `conftest.py` - Shared pytest fixtures (test images)
- `test_core.py` - Tests for the main `asciify()` function
- `test_process.py` - Tests for the `ImgProcessor` class
- `test_renderer.py` - Tests for the `Renderer` class

## Running Tests

Install test dependencies.

```bash
pip install -e ".[dev]"
```

Run all tests.

```bash
pytest
```

Run with coverage report.

```bash
pytest --cov=asciify --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage.

Run specific test file.

```bash
pytest tests/test_core.py
```

Run specific test.

```bash
pytest tests/test_core.py::TestAsciify::test_asciify_returns_string
```
