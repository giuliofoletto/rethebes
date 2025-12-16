"""
Test facility for run mode.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import time
from pathlib import Path

import pytest

from rethebes.run import run


# Tests of running logic
def test_typical():
    configuration = {
        "instruments": ["loader", "sensor"],
        "loader": [
            {
                "target_cores": "all",
                "target_loads": 0,
                "duration": 0.5,
                "sampling_interval": 0.1,
            }
        ],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": False,
        },
    }
    run(configuration)
    # No assert since we are only testing for exceptions here


def test_cannot_read_temperature_critical(caplog):
    # Note: This test succeeds if there is a critical error in reading the temperature
    # This happens if the test is run without admin privileges
    # This means that this test should be run without admin privileges (otherwise there is no error and the test fails)
    configuration = {
        "instruments": ["sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": False,
            "write": False,
        },
    }
    caplog.set_level(logging.CRITICAL)
    run(configuration)
    assert "Could not read temperature" in caplog.text


def test_time():
    configuration = {
        "instruments": ["timer", "sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": False,
        },
        "timer": {"duration": 1},
    }
    start = time.time()
    run(configuration)
    stop = time.time()
    assert (
        stop - start < configuration["timer"]["duration"] + 3
    )  # Allow 3 seconds of grace time


def test_write():
    configuration = {
        "instruments": ["timer", "sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": True,
            "file_name": "test_write.csv",
        },
        "timer": {"duration": 1},
    }
    run(configuration)
    path = Path.cwd() / configuration["sensor"]["file_name"]
    assert path.exists()
    path.unlink()  # Clean up
