"""
Util functions to read and analyze data files.

Authors: Giulio Foletto.
License: See project-level license file.
"""

import matplotlib.dates as mdates
import numpy as np
import pandas as pd

window_in_seconds = 5


def read_data_from_file(file_name):
    return pd.read_csv(file_name, delimiter=",", parse_dates=["Time"])


def check_if_data_complete(data):
    return not data["Temperature CPU Package"].isnull().values.any()


date_format = mdates.DateFormatter("%H:%M:%S")


def get_number_of_cores(data):
    return (",").join(list(data.columns)).count(
        "Temperature CPU Core"
    ) // 2  # //2 because of presence of distance to tjmax


def get_best_tick_interval(data):
    tot_time = (data["Time"].max() - data["Time"].min()) / (np.timedelta64(1, "s"))
    if tot_time > 10:
        tick_interval = int(tot_time / 10)
    else:
        tick_interval = 1
    return tick_interval


def get_columns_for_labels(num_labels):
    if num_labels <= 3:
        return num_labels
    if num_labels % 2 == 0:
        return num_labels // 2
    else:
        return (num_labels + 1) // 2


def format_standard_axis(data, axis):
    axis.autoscale(tight=True)
    axis.grid()
    _, labels = axis.get_legend_handles_labels()
    axis.legend(
        ncol=get_columns_for_labels(len(labels)),
        loc="center",
        bbox_to_anchor=(0.5, 1.06),
        fontsize="x-small",
    )
    axis.xaxis.set_major_formatter(date_format)
    axis.xaxis.set_major_locator(
        mdates.SecondLocator(interval=get_best_tick_interval(data))
    )
    axis.set_xlabel("Time")


def get_average_load_core(data, core_index):
    valid_columns = []
    for column in data.columns:
        if ("Load CPU Core #" + str(core_index) + " Thread #") in column:
            valid_columns.append(column)
    return data[valid_columns].mean(axis=1)


def analyze_temp_vs_load(data):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(window_in_seconds / delta_t)
    x = data["Load CPU Total"].rolling(window).mean()
    y = data["Temperature Core Average"].rolling(window).mean()
    # Use range rather than percentiles because non-uniform distributions are more likely than outliers
    l95 = x.min() + 0.95 * (x.max() - x.min())
    l05 = x.min() + 0.05 * (x.max() - x.min())
    t_for_l95 = y[x > l95].mean()
    t_for_l05 = y[x < l05].mean()
    std_t_for_l95 = y[x > l95].std()
    std_t_for_l05 = y[x < l05].std()
    result = dict(
        l95=l95,
        l05=l05,
        t_for_l95=t_for_l95,
        std_t_for_l95=std_t_for_l95,
        t_for_l05=t_for_l05,
        std_t_for_l05=std_t_for_l05,
    )
    return result


def analyze_temp_vs_power(data):
    delta_t = data["Time"].diff().mean() / np.timedelta64(1, "s")
    window = int(window_in_seconds / delta_t)
    x = data["Power CPU Cores"].rolling(window).mean()
    y = data["Temperature Core Average"].rolling(window).mean()
    sigmay = data["Temperature Core Average"].rolling(window).std()
    # Use range rather than percentiles because non-uniform distributions are more likely than outliers
    p95 = x.min() + 0.95 * (x.max() - x.min())
    p05 = x.min() + 0.05 * (x.max() - x.min())
    t_for_p95 = y[x > p95].mean()
    t_for_p05 = y[x < p05].mean()
    std_t_for_p95 = y[x > p95].std()
    std_t_for_p05 = y[x < p05].std()
    valid = ~(np.isnan(x) | np.isnan(y))
    (m, q), cov = np.polyfit(x[valid], y[valid], 1, w=1 / sigmay[valid], cov="unscaled")
    c = 1 / m
    sigma_c = c**2 * np.sqrt(cov[0, 0])
    result = dict(
        p95=p95,
        p05=p05,
        m=m,
        sigma_m=np.sqrt(cov[0, 0]),
        q=q,
        sigma_q=np.sqrt(cov[1, 1]),
        c=c,
        sigma_c=sigma_c,
        t_for_p95=t_for_p95,
        std_t_for_p95=std_t_for_p95,
        t_for_p05=t_for_p05,
        std_t_for_p05=std_t_for_p05,
    )
    return result
