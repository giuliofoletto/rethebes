default_configuration = {
    "instruments": ["loader", "sensor"],
    "loader": [
        {
            "target_cores": "all",
            "target_loads": 0,
            "duration": 2,
            "sampling_interval": 0.1
        },
        {
            "target_cores": "all",
            "target_loads": 10,
            "duration": 10,
            "sampling_interval": 0.1
        },
        {
            "target_cores": "all",
            "target_loads": 0,
            "duration": 2,
            "sampling_interval": 0.1
        }
    ],
    "sensor": {
        "sampling_interval": 0.1
    }
}