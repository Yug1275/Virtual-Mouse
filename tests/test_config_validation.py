# tests/test_config_validation.py
# PURPOSE: Verify that validate_settings() correctly catches bad configs.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import config.settings as settings


def test_valid_config():
    """With default settings.py values, validation should pass silently."""
    try:
        settings.validate_settings()
        print("PASS: Default settings are valid (no exception raised).")
    except ValueError as e:
        print(f"FAIL: Default settings raised an error unexpectedly:\n{e}")


def test_invalid_smoothing_factor():
    """Temporarily break SMOOTHING_FACTOR and confirm it's caught."""
    original = settings.SMOOTHING_FACTOR
    settings.SMOOTHING_FACTOR = 0  # invalid: must be > 0

    try:
        settings.validate_settings()
        print("FAIL: Invalid SMOOTHING_FACTOR was NOT caught.")
    except ValueError as e:
        print(f"PASS: Invalid SMOOTHING_FACTOR correctly caught:\n  {e}")
    finally:
        settings.SMOOTHING_FACTOR = original  # restore original value


def test_invalid_frame_reduction():
    """Temporarily break FRAME_REDUCTION and confirm it's caught."""
    original = settings.FRAME_REDUCTION
    settings.FRAME_REDUCTION = 1000  # invalid: way too large

    try:
        settings.validate_settings()
        print("FAIL: Invalid FRAME_REDUCTION was NOT caught.")
    except ValueError as e:
        print(f"PASS: Invalid FRAME_REDUCTION correctly caught:\n  {e}")
    finally:
        settings.FRAME_REDUCTION = original


if __name__ == "__main__":
    print("Running config validation tests...\n")
    test_valid_config()
    test_invalid_smoothing_factor()
    test_invalid_frame_reduction()