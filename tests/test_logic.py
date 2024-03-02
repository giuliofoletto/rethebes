"""
Test facility.

Authors: Giulio Foletto.
"""

import pytest
import logging
from rethebes.logic import main, process_configuration, default_configuration

# Tests of main logic
def test_typical():
    configuration = {
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
            "accept_incomplete_data": True
        }
    }
    main(configuration)
    # No assert since we are only testing for exceptions here

def test_cannot_read_temperature_critical(caplog):
    # Note: This test succeeds if there is a critical error in reading the temperature
    # This happens if the test is run without admin privileges
    configuration = {
        "loader": [
            {
                "target_cores": "all",
                "target_loads": 0,
                "duration": 0.5,
                "sampling_interval": 0.1
            }
        ],
        "sensor": {
            "sampling_interval": 0.1
        }
    }
    caplog.set_level(logging.CRITICAL)
    main(configuration)
    assert "Could not read temperature" in caplog.text

def test_process_configuration():
    configuration = {
        "instruments": ["loader", "sensor"]
    }
    configuration = process_configuration(configuration)

    for instrument in configuration["instruments"]:
        assert configuration[instrument] == default_configuration[instrument]


