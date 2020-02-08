# MPFS2 file extractor

![](https://github.com/rene-d/mpfs2/workflows/Publish%20to%20PyPI/badge.svg)
[![pyi](https://img.shields.io/pypi/v/mpfs2.svg)](https://pypi.python.org/pypi/mpfs2)
[![pyi](https://img.shields.io/pypi/pyversions/mpfs2.svg)](https://pypi.python.org/pypi/mpfs2)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Extract files from a Microchip Proprietary File System (MPFS2).

## Usage

### Install with pip

```bash
pip3 install mpfs2
```

### Commandline

```
Usage: mpfs2.py [OPTIONS] INPUT

Options:
  -v, --verbose           be verbose
  -x, --extract           extract files
  -a, --all               also extract files with no name
  -l, --list              list files
  -d, --extract-dir PATH  directory to extract files
  --help                  Show this message and exit.
```

## License

MIT
