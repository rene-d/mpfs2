#!/usr/bin/env python3

#
# MPFS Structure:
#     [M][P][F][S]
#     [BYTE Ver Hi][BYTE Ver Lo][WORD Number of Files]
#     [Name Hash 0][Name Hash 1]...[Name Hash N]
#     [File Record 0][File Record 1]...[File Record N]
#     [String 0][String 1]...[String N]
#     [File Data 0][File Data 1]...[File Data N]
#
# Name Hash (2 bytes):
#     hash = 0
#     for each(byte in name)
#         hash += byte
#         hash <<= 1
#
#     Technically this means the hash only includes the
#     final 15 characters of a name.
#
# File Record Structure (22 bytes):
#     [DWORD String Ptr][DWORD Data Ptr]
#     [DWORD Len][DWORD Timestamp][DWORD Microtime]
#     [WORD Flags]
#
#     Pointers are absolute addresses within the MPFS image.
#     Timestamp is the UNIX timestamp
#     Microtime is currently unimplemented
#
# String Structure (1 to 64 bytes):
#     ["path/to/file.ext"][0x00]
#
# File Data Structure (arbitrary length):
# 		[File Data]
#
# Unlike previous versions, there are no delimiters.
#
# Name hash is calculated as follows:
#      hash = 0
#      for each(byte in name)
#          hash += byte, hash <<= 1
#
# When a file has an index, that index file has no file name,
# but is accessible as the file immediately following in the image.
#
# Current version is 2.1
#

# ref: https://github.com/x893/Microchip/blob/master/Microchip/TCPIP%20Stack/MPFS2.c

import datetime
import pathlib
import struct
from collections import namedtuple

import click

FileRecord = namedtuple("FileRecord", ["StringPtr", "DataPtr", "Len", "Timestamp", "Microtime", "Flags"])


@click.command()
@click.argument("mpfs2_file", type=click.File("rb"), nargs=1)
@click.option("-v", "--verbose", help="be verbose", is_flag=True)
@click.option("-x", "--extract", help="extract files", is_flag=True)
@click.option("-a", "--all", "noname_files", help="also extract files with no name", is_flag=True)
@click.option("-l", "--list", "list_files", help="list files", is_flag=True)
@click.option("-d", "--extract-dir", default="export", help="directory to extract files", type=click.Path())
def main(mpfs2_file, verbose, extract, noname_files, list_files, extract_dir):

    fs = mpfs2_file.read()

    signature = fs[0:4]
    if signature != b"MPFS":
        print("File is not a MPFS filesystem")
        return 2

    ver_hi = fs[4]
    ver_lo = fs[5]
    print(f"Version: {ver_hi}.{ver_lo}")

    (n,) = struct.unpack("<H", fs[6:8])
    print(f"Number of files: {n}")

    offset = 8
    name_hash = [0] * n
    for i in range(n):
        (name_hash[i],) = struct.unpack("<H", fs[offset : offset + 2])
        offset += 2

    record = [None] * n
    for i in range(n):
        record[i] = FileRecord._make(struct.unpack("<IIIIIH", fs[offset : offset + 22]))
        offset += 22

    def get_string(fs, ptr, hex_name=False):
        if fs[ptr] == 0:
            if hex_name:
                return f"{ptr:06X}"
            else:
                return "<no name>"
        s = ""
        for i in fs[ptr:]:
            if i == 0:
                break
            elif i < 32:
                s += f"<{i}>"
            else:
                s += chr(i)
        return s

    export = pathlib.Path(extract_dir)

    for i, r in enumerate(record):

        if fs[r.StringPtr] == 0 and not noname_files:
            continue

        ts = datetime.datetime.fromtimestamp(r.Timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")

        if list_files:
            if verbose:
                print()
                print(f"FileRecord {i}:")
                print("    .StringPtr =", r.StringPtr, get_string(fs, r.StringPtr))
                print("    .DataPtr   =", r.DataPtr)
                print("    .Len       =", r.Len)
                print("    .Timestamp =", ts)
                print("    .Flags     =", r.Flags)
            else:
                print(f"{i:4d}   {r.Len:8d}   {ts}   {get_string(fs, r.StringPtr)}")

        if extract:
            f = export / get_string(fs, r.StringPtr, True)
            f.parent.mkdir(exist_ok=True, parents=True)

            f.write_bytes(fs[r.DataPtr : r.DataPtr + r.Len])
            if verbose:
                print(f"extracted: {f.as_posix()} {r.Len} bytes")


if __name__ == "__main__":
    main()
