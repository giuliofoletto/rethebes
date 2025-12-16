"""
Test facility for handling configs.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import logging
import time
from pathlib import Path

import pytest

from rethebes.run import default_configuration, process_configuration


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
