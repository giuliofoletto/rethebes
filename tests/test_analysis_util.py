"""
Test facility for the util functions in the analysis subpackage.

Authors: Giulio Foletto.
License: See project-level license file.
"""

from pathlib import Path

import pytest

from rethebes.analysis.util import (
    analyze_temp_vs_load,
    analyze_temp_vs_power,
    check_if_data_complete,
    get_average_load_core,
    get_best_tick_interval,
    get_number_of_cores,
    read_data_from_file,
)

TEST_DATA_DIR = Path(__file__).parent / "data"


def test_read_data_from_file():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    assert not data.empty
    assert "Time" in data.columns
    assert "Temperature CPU Package" in data.columns


def test_check_if_data_complete():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    assert check_if_data_complete(data)
    # TODO add a test with incomplete data


def test_get_number_of_cores():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    num_cores = get_number_of_cores(data)
    assert num_cores == 6


def test_get_best_tick_interval():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    tick_interval = get_best_tick_interval(data)
    assert tick_interval == 65  # For this specific file


def test_get_average_load_core():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    avg_loads = []
    num_cores = get_number_of_cores(data)
    for i in range(num_cores):
        avg_load = get_average_load_core(data, i + 1)
        avg_loads.append(avg_load)
    expected_means = [
        50.67147708767243,
        49.96222525762238,
        50.37755893268658,
        49.94833086820049,
        50.16771271674688,
        50.05873608034076,
    ]  # For the specific file
    for i in range(num_cores):
        assert avg_loads[i].mean() == pytest.approx(
            expected_means[i], 1e-3
        )  # mean because the result is still a Series


def test_analyze_temp_vs_load():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    results = analyze_temp_vs_load(data)
    expected_results = dict(
        l95=95.15949302249484,
        l05=8.03108459048801,
        t_for_l95=79.15883150671281,
        std_t_for_l95=1.474786745973586,
        t_for_l05=40.248074937574934,
        std_t_for_l05=2.40964291980774,
    )
    for key in expected_results:
        assert results[key] == pytest.approx(expected_results[key], 1e-3)


def test_analyze_temp_vs_power():
    file_path = TEST_DATA_DIR / "example_full.csv"
    data = read_data_from_file(file_path)
    results = analyze_temp_vs_power(data)
    expected_results = dict(
        p95=74.56014847738875,
        p05=4.655501124097241,
        t_for_p95=81.29907365587022,
        std_t_for_p95=0.8097969318015877,
        t_for_p05=39.63919428824214,
        std_t_for_p05=1.3589345627673284,
        m=0.5675147033877365,
        sigma_m=0.0008319073896130219,
        q=38.92118408040697,
        sigma_q=0.05329613739690532,
        c=1.7620688839083376,
        sigma_c=0.002582978232599202,
    )
    for key in expected_results:
        assert results[key] == pytest.approx(expected_results[key], 1e-3)
