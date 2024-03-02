"""
Test facility.

Authors: Giulio Foletto.
"""

import pytest
import os
import logging
import time
from rethebes.logic import main, process_configuration, default_configuration

# Tests of main logic
def test_typical():
    configuration = {
        "instruments": ["loader", "sensor"],
        "loader": [
            {
                "target_cores": "all",
                "target_loads": 0,
                "duration": 0.5,
                "sampling_interval": 0.1
            }
        ],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": False
        }
    }
    main(configuration)
    # No assert since we are only testing for exceptions here

def test_cannot_read_temperature_critical(caplog):
    # Note: This test succeeds if there is a critical error in reading the temperature
    # This happens if the test is run without admin privileges
    configuration = {
        "instruments": ["sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": False,
            "write": False,
        }
    }
    caplog.set_level(logging.CRITICAL)
    main(configuration)
    assert "Could not read temperature" in caplog.text

def test_time():
    configuration = {
        "instruments": ["timer", "sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": False,
        },
        "timer": {
            "duration": 1
        }
    }
    start = time.time()
    main(configuration)
    stop = time.time()
    assert stop - start < configuration["timer"]["duration"] + 3 # Allow 3 seconds of grace time

def test_write():
    configuration = {
        "instruments": ["timer", "sensor"],
        "sensor": {
            "sampling_interval": 0.1,
            "accept_incomplete_data": True,
            "write": True,
            "file_name": "test_write.csv"
        },
        "timer": {
            "duration": 1
        }
    }
    main(configuration)
    path = os.path.join("./", configuration["sensor"]["file_name"])
    assert os.path.exists(path)
    os.remove(path)

def test_process_configuration():
    configuration = {
        "instruments": "auto"
    }
    configuration = process_configuration(configuration)

    assert configuration["instruments"] == default_configuration["instruments"]
    assert "timer" not in configuration["instruments"]
    assert configuration["master"] == "loader"
    for instrument in configuration["instruments"]:
        assert configuration[instrument] == default_configuration[instrument]

    configuration = {
        "instruments": ["sensor"]
    }
    configuration = process_configuration(configuration)

    assert "timer" in configuration["instruments"]
    assert "loader" not in configuration["instruments"]
    assert configuration["master"] == "timer"
    for instrument in configuration["instruments"]:
        assert configuration[instrument] == default_configuration[instrument]


