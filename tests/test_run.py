"""
Test facility for run mode.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import time
from pathlib import Path

import pytest

from rethebes.run import default_configuration, process_configuration, run


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


def test_process_configuration():
    configuration = {"instruments": "auto"}
    configuration = process_configuration(configuration)

    assert configuration["instruments"] == default_configuration["instruments"]
    assert "timer" not in configuration["instruments"]
    assert configuration["master"] == "loader"
    for instrument in configuration["instruments"]:
        assert configuration[instrument] == default_configuration[instrument]

    configuration = {"instruments": ["sensor"]}  # No master
    configuration = process_configuration(configuration)

    assert "timer" in configuration["instruments"]
    assert "loader" not in configuration["instruments"]
    assert configuration["master"] == "timer"
    for instrument in configuration["instruments"]:
        assert configuration[instrument] == default_configuration[instrument]

    configuration = {
        "instruments": ["sensor", "loader"],
        "sensor": {"write": False},  # Incomplete settings
        "loader": [{"duration": 1}],
    }
    configuration = process_configuration(configuration)

    assert "timer" not in configuration["instruments"]
    assert configuration["master"] == "loader"
    for k in default_configuration["sensor"]:
        assert k in configuration["sensor"]
        if k != "write":
            assert configuration["sensor"][k] == default_configuration["sensor"][k]
    assert configuration["sensor"]["write"] == False
    default_load = default_configuration["loader"][0]
    for k in default_load:
        assert k in configuration["loader"][0]
        if k != "duration":
            assert (
                configuration["loader"][0][k] == default_configuration["loader"][0][k]
            )
    assert configuration["loader"][0]["duration"] == 1
