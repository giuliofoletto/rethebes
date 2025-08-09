## Configuration Guide

In this folder you can find some example configuration files.
At the moment, these are:

-   [`idle.json`](idle.json): Only log the sensor measurements without stressing the CPU in any way until CTRL+C is pressed.
-   [`long.json`](long.json): Stress all cores from 0 to 100% and back, with 10% steps of 30 seconds each.
    This takes approximately 10m30s.
-   [`short.json`](short.json): For testing purposes, use the `loader` module but stress the CPU at the minimum level for 5 seconds, without saving files.

You can create your custom configuration files based on these.
For example, to stress all cores to 50% for 10 seconds, and then cores 1 to 35% and 4 to 65% for 20 seconds, use

```json
{
    "instruments": ["sensor", "loader"],
    "analyze": true,
    "loader": [
        {
            "target_cores": "all",
            "target_loads": 50,
            "duration": 10,
            "sampling_interval": 0.1
        },
        {
            "target_cores": [1, 4],
            "target_loads": [35, 65],
            "duration": 20,
            "sampling_interval": 0.1
        }
    ],
    "sensor": {
        "sampling_interval": 0.1,
        "file_name": "auto"
    }
}
```

Note that cores are numbered from 1, whereas some other programs might count them from 0.

The `instruments` you select direct the operation of the test.
Available `instruments` are:

-   `sensor`: Measures temperature and other parameters.
-   `loader`: Controls the load on the CPU for a specified time.
-   `timer`: Allows to set a duration for the test if `loader` is not present.

Typically, `sensor` and `loader` should be included.

The key `"analyze": true`, specifies that you want to visualize the results after the measurement.
If you set it to `false`, you can always analyze the results later using `rethebes analyze <output-file>`.

In `sensor`, use `"file_name": "auto"` to save the measured results to the default folder (`~/.rethebes/output/`) and name them with the time stamp corresponding to the start of the test.
Alternatively, you can specify a file path using this key.
If you do not want to write the results to file, use `"write": false`.

Other keys to configure the `instruments` should be self-explanatory from the examples.
