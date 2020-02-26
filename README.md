# MPFS2 file extractor

![](https://github.com/rene-d/mpfs2/workflows/Publish%20to%20PyPI/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/53cc11afa1b243959d3c6401cc6d8392)](https://app.codacy.com/manual/rene-d/mpfs2?utm_source=github.com&utm_medium=referral&utm_content=rene-d/mpfs2&utm_campaign=Badge_Grade_Settings)
[![pyi](https://img.shields.io/pypi/v/mpfs2.svg)](https://pypi.python.org/pypi/mpfs2)
[![pyi](https://img.shields.io/pypi/pyversions/mpfs2.svg)](https://pypi.python.org/pypi/mpfs2)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

List contents and extract files from a Microchip Proprietary File System (MPFS2).

## Usage

### Install with pip

```bash
pip3 install -U mpfs2
```

### Commandline

```text
Usage: mpfs2 [OPTIONS] MPF2_FILE

Options:
  -v, --verbose           be verbose
  -x, --extract           extract files
  -l, --list              list files
  -V, --variables         list dynamic variables
  -d, --extract-dir PATH  directory to extract files
  --help                  Show this message and exit.
```

## License

MIT
