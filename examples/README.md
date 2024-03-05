## Configuration Guide

In this folder you can find some example configuration files.
At the moment, these are:

-   [`idle.json`](idle.json): Just log the sensor measurements without stressing the CPU in any way for 60 seconds.
-   [`long.json`](long.json): Stress all cores from 0 to 100% and back, for 30 seconds each.
    This lasts approximately 10m30s.
-   [`short.json`](short.json): For testing purposes, use the `loader` module but stress the CPU at the minimum level for 5 seconds, without saving files.

You can create your custom configuration files based on these.
For example, to stress all cores to 50% for 10 seconds, and then cores 1 to 35% and 4 a 65% for 20 seconds, use

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

Note that cores are numbered from 1 here.

The key `"analyze": true`, specifies that you want to visualize the results after the measurement.
Otherwise the measurement ends and you can visualize the results later using `rethebes analyze <output-file>`.
