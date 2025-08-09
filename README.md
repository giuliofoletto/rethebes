# rethebes

Repeatable thermal benchmarks.

`rethebes` is a command-line utility that runs a repeatable benchmark of the CPU temperature under user-configurable load conditions.

## Motivation

It is often difficult to test the temperature of your hardware in a scientific and repeatable way.
Some programs measure the temperature, some stress-test the CPU, some even allow both, but require manual operation.

With `rethebes`, you can configure your stress-test and then run it from the command line.
Since running the test requires no user action besides launching a command, the test results are more consistent than those obtained by manually running a stress test and a temperature logger at the same time.
With this repeatability, you can easily track and monitor the thermal performance of your system.

## Features

Some notable features of `rethebes` are:

-   Granular control of the CPU load, per physical core.
-   All the measurements offered by [`LibreHardwareMonitorLib`](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor), such as temperature, load, power, frequency.
-   Data saved in `.csv` format like that used by `LibreHardwareMonitor`.
-   Visualization of measurement results after the test.

## Requirements

`rethebes` should work on Windows 10+ and python 3.8+.
It also requires [.NET Framework 4.7](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net47) to be installed (this is commonly true on Windows).
All the other dependencies are automatically installed during the installation of `rethebes`.
Note that `rethebes` uses [`PyHardwareMonitor`](https://github.com/snip3rnick/PyHardwareMonitor), a wrapper for `LibreHardwareMonitorLib`, which is downloaded automatically from pypi.

## Installation

You can install `rethebes` from github via `pip` or (recommended) [`pipx`](https://github.com/pypa/pipx):

```
pipx install git+https://github.com/giuliofoletto/rethebes
```

## Removal

If you want to uninstall `rethebes`, you can do so with command:

```
pipx uninstall rethebes
```

Note that, unless you specify otherwise in the configuration file, running `rethebes` creates the folder `~/.rethebes`, which is not deleted by `pipx` when you uninstall `rethebes`.
You can delete it manually with

```
rm ~/.rethebes -r -Force
```

## Usage

In an elevated terminal (required to access temperature sensors), run:

```
rethebes run <config-file>
```

where `<config-file>` is the path of a configuration file.
See [examples/README.md](examples/README.md) for a guide about configuration files, and pre-made examples.

If your configuration instructed `rethebes` to save the measurements results, you can visualize them with:

```
rethebes analyze <output-file>
```

You can also view a simple comparison of multiple files with:

```
rethebes compare <output-file-1> <output-file-2> ...
```

Analysis and comparison do not need an elevated terminal.

## Tricks

For convenience, if you place your configuration file in the default folder (`~/.rethebes/config/`), you can invoke it via name only, without necessarily including the full path or the extension.
For instance:

```
rethebes run short
```

will work if file `~/.rethebes/config/short.json` exists.

You can do the same for output files (in `~/.rethebes/output/`):

```
rethebes analyze data
```

will work if file `~/.rethebes/output/data.csv` exists.

## Development

While developing `rethebes`, it is best to install it in an editable manner so that code changes are instantly available in the executed code without reinstallation:

```
pip install -e .
```

The `tests` folder contains some tests that should be run in a non-elevated terminal with `pytest`.

## Attribution

The module that loads the CPU uses [code](https://github.com/GaetanoCarlucci/CPULoadGenerator/) by Gaetano Carlucci and Giuseppe Cofano (MIT licensed).
In addition to `LibreHardwareMonitorLib` (MPL licensed), the code depends on other open source python packages that are downloaded automatically during installation.
See [pyproject.toml](pyproject.toml) for the list.
