# rethebes

Repeatable thermal benchmarks.
`rethebes` is a command-line utility that runs a repeatable benchmark of the CPU temperature under user-configurable load conditions.

## Requirements and installation

`rethebes` has only been tested on Windows 10 and python 3.8.
It should also be compatible with more recent Windows and python versions.

Internally, `rethebes` uses [`LibreHardwareMonitorLib`](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor), which is not distributed with `rethebes` and must be installed separately. To do so, you must:

1. Download it from the [Releases page on github](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/tag/v0.9.3).
2. Add the directory where you have extracted `LibreHardwareMonitorLib.dll` to your `PYTHONNET` environment variable in Windows.

Note that you also need some version of the .NET runtime, but that is commonly installed in Windows.

Then, you can install `rethebes` from github via `pip` or (recommended) [`pipx`](https://github.com/pypa/pipx).

```
pipx install git+https://github.com/giuliofoletto/rethebes
```

## Usage

In an elevated terminal (required to access temperature sensors), run:

```
rethebes run <config-file>
```

where `<config-file>` is the path of a configuration file.
See [examples/README.md](examples/README.md) for a guide about configuration files, and pre-made examples.

Note that unless you specify otherwise in the configuration file, running `rethebes` creates the folder `~/.rethebes`, which is not deleted by `pipx` during if you uninstall `rethebes`.

Assuming your configuration file instructed `rethebes` to save the measurements results, you can visualize them with

```
rethebes analyze <output-file>
```

## Tricks

For convenience, if you place your configuration file in the default folder (`~/.rethebes/config/`), you can invoke it via name only, without necessarily including the full path or the extension.
For instance

```
rethebes run short
```

will work if file `~/.rethebes/config/short.json` exists.

You can do the same for output files (in `~/.rethebes/output/`):

```
rethebes analyze foobar
```

will work if file `~/.rethebes/output/foobar.csv` exists.

## Attribution

The package that loads the CPU uses [code](https://github.com/GaetanoCarlucci/CPULoadGenerator/) by Gaetano Carlucci and Giuseppe Cofano (MIT licensed).
In addition to `LibreHardwareMonitorLib` (MPL licensed), the code depends on other open source python packages that are downloaded automatically during installation.
See [setup.py](setup.py) for the list.
