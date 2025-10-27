# Testing Guide

This document explains the test structure and how to run different types of tests in this project.

## Test File Overview

The project contains different types of test files, each serving a specific purpose:

### 1. Unit Tests (Automated)

These follow the standard `unittest` framework and can be run automatically:

- **`test_api.py`**: Tests for the Flask API endpoints
  - Tests `/detect` endpoint with valid images
  - Tests error handling when no file is provided
  - Uses proper server lifecycle management

- **`test_realtime.py`**: Tests for real-time detection functionality
  - Tests frame processing with valid images
  - Tests error handling with invalid inputs
  - Validates output structure and types

**Running Unit Tests:**
```bash
# Run all unit tests
python -m unittest discover -s . -p "test_*.py" -v

# Run specific test file
python -m unittest test_api.TestAPI -v
python -m unittest test_realtime.TestRealtime -v

# Run individual test case
python -m unittest test_api.TestAPI.test_detect_endpoint_with_valid_image
```

### 2. Functional Test Scripts (Interactive)

These are utility scripts for manual testing and validation:

- **`test_quick.py`**: Quick validation of environment and dependencies
  - Tests dependency imports (PyTorch, Transformers, OpenCV, etc.)
  - Tests DINO pipeline initialization
  - Tests sample image detection
  - **Usage:** `python test_quick.py`

### 3. Benchmark and Analysis Scripts

These are tools for performance testing and parameter optimization:

- **`test_multi_lights.py`**: Multi-light scene detection comparison
  - Compares different detection configurations
  - Batch testing across multiple images
  - Generates visualization and comparison reports
  - **Usage:** 
    ```bash
    # Single image test
    python test_multi_lights.py --image path/to/image.jpg
    
    # Batch test
    python test_multi_lights.py --batch --samples 10
    ```

- **`test_threshold_fine.py`**: Fine-grained threshold optimization
  - Tests specific threshold ranges
  - Statistical analysis of detection confidence
  - Visualization of results
  - **Usage:**
    ```bash
    # Single image with custom thresholds
    python test_threshold_fine.py --image path/to/image.jpg --thresholds 0.12 0.15 0.18
    
    # Batch test with default thresholds
    python test_threshold_fine.py --batch --samples 10
    ```

## Test Data Requirements

Tests require sample images from one of these locations:
- `data/nyu_data/data/0001.jpg`
- `data/yolo_dataset/images/val/val_00000.jpg`
- `data/nyu_data/data/nyu2_test/0001.jpg`

Tests will automatically search for available test images in these locations.

## Continuous Integration

For CI/CD pipelines, run only the automated unit tests:

```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests only (skip benchmark scripts)
python -m unittest test_api test_realtime
```

## Test Coverage

### Current Test Coverage:

**API Tests (`test_api.py`):**
- ✅ Valid image detection
- ✅ Missing file error handling
- ✅ Server lifecycle management
- ✅ Response structure validation

**Realtime Tests (`test_realtime.py`):**
- ✅ Valid frame processing
- ✅ Invalid input error handling
- ✅ Empty image error handling
- ✅ Output type validation

### Areas for Future Testing:

- [ ] Model loading with different configurations
- [ ] Edge cases for image preprocessing
- [ ] Performance benchmarks under load
- [ ] Memory usage monitoring
- [ ] GPU vs CPU execution paths
- [ ] Batch processing tests
- [ ] Integration tests with full pipeline

## Best Practices

1. **Unit Tests**:
   - Keep tests fast and focused
   - Mock heavy dependencies when possible
   - Test one thing per test method
   - Use descriptive test names

2. **Functional Tests**:
   - Provide clear output and progress indicators
   - Handle missing dependencies gracefully
   - Document expected behavior

3. **Benchmark Scripts**:
   - Save results for later comparison
   - Document test parameters
   - Provide summary statistics

## Troubleshooting

### Common Issues:

**Import Errors:**
```bash
# Install missing dependencies
pip install -r requirements.txt
```

**No Test Images Found:**
```bash
# Download test data
python step1_download_data.py
```

**Server Startup Timeout (test_api.py):**
- Ensure port 5000 is not already in use
- Check if models are cached (first run may be slower)

**GPU Out of Memory:**
- Reduce batch size in benchmark scripts
- Use smaller model variants
- Test on CPU instead: set device to 'cpu' in code

## Contributing New Tests

When adding new tests:

1. **For Unit Tests**: Add to `test_api.py` or `test_realtime.py`
2. **For Utilities**: Create new files with clear documentation
3. **Update This Guide**: Document the new test's purpose and usage
4. **Follow Naming Convention**: 
   - Unit tests: `test_<module>.py` with unittest framework
   - Utilities: `test_<purpose>.py` with clear header documentation

## Test Maintenance

- Review and update tests when API changes
- Keep test data lightweight and version-controlled
- Remove or update obsolete tests
- Document known issues or flaky tests
