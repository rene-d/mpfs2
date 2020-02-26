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
import gzip
import pathlib
import struct
import sys
from collections import namedtuple

import click

MPFS2_FLAG_ISZIPPED = 0x0001  # Indicates a file is compressed with GZIP compression
MPFS2_FLAG_HASINDEX = 0x0002  # Indicates a file has an associated index of dynamic variables

FileRecord = namedtuple("FileRecord", ["StringPtr", "DataPtr", "Len", "Timestamp", "Microtime", "Flags"])


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


def get_var(fs, ptr):
    if fs[ptr] != ord("~"):
        return "<no var>"
    s = ""
    for i in fs[ptr + 1 :]:
        if i == ord("~"):
            break
        s += chr(i)
    return s


def find_variables(fs, record):

    variables = {}
    it = iter(record)
    try:
        while True:
            r = next(it)
            if r.Flags & MPFS2_FLAG_HASINDEX != MPFS2_FLAG_HASINDEX:
                continue

            v = next(it)

            for i in range(v.DataPtr, v.DataPtr + v.Len, 8):
                offset, num_var = struct.unpack("II", fs[i : i + 8])

                var_name = get_var(fs, r.DataPtr + offset)
                if num_var not in variables:
                    variables[num_var] = var_name
                else:
                    if variables[num_var] != var_name:
                        print(f"Bad index variable", file=sys.stderr)
                        raise StopIteration

    except StopIteration:
        pass

    return variables


@click.command()
@click.argument("mpfs2_file", type=click.File("rb"), nargs=1)
@click.option("-v", "--verbose", help="be verbose", is_flag=True)
@click.option("-x", "--extract", help="extract files", is_flag=True)
@click.option("-l", "--list", "list_files", help="list files", is_flag=True)
@click.option("-V", "--variables", "list_variables", help="list dynamic variables", is_flag=True)
@click.option("-d", "--extract-dir", default="export", help="directory to extract files", type=click.Path())
def main(mpfs2_file, verbose, extract, list_files, list_variables, extract_dir):

    fs = mpfs2_file.read()

    signature = fs[0:4]
    if signature != b"MPFS":
        print("File is not a MPFS filesystem")
        return 2

    # process filesystem header
    ver_hi = fs[4]
    ver_lo = fs[5]
    (n,) = struct.unpack("<H", fs[6:8])

    offset = 8
    name_hash = [0] * n
    for i in range(n):
        (name_hash[i],) = struct.unpack("<H", fs[offset : offset + 2])
        offset += 2

    record = [None] * n
    for i in range(n):
        record[i] = FileRecord._make(struct.unpack("<IIIIIH", fs[offset : offset + 22]))
        offset += 22

    n_idx = 0
    for r in record:
        if r.Flags & MPFS2_FLAG_HASINDEX == MPFS2_FLAG_HASINDEX:
            n_idx += 1

    # find all dynamic variables
    variables = find_variables(fs, record)

    print(f"Version: {ver_hi}.{ver_lo}")
    print(f"Number of files: {n} ({n-n_idx} regular, {n_idx} index)")
    print(f"Number of dynamic variables: {len(variables)}")

    export = pathlib.Path(extract_dir)

    next_is_indexfile = None
    filename = None

    for i, r in enumerate(record):

        if next_is_indexfile is None:
            if fs[r.StringPtr] == 0:
                print(f"Bad file entry {i}: should have a name", i, file=sys.stderr)
                break
            filename = get_string(fs, r.StringPtr)
        else:
            if fs[r.StringPtr] != 0:
                print(f"Bad file entry {i}: should be an index", i, file=sys.stderr)
                break
            filename = next_is_indexfile + "-index"

        if list_files:
            timestamp = datetime.datetime.fromtimestamp(r.Timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")

            if verbose:
                flag = []
                if r.Flags & MPFS2_FLAG_HASINDEX == MPFS2_FLAG_HASINDEX:
                    flag.append("HASINDEX")
                if r.Flags & MPFS2_FLAG_ISZIPPED == MPFS2_FLAG_ISZIPPED:
                    flag.append("ISZIPPED")

                print()
                print(f"FileRecord {i}:")
                print("    .StringPtr =", r.StringPtr, filename)
                print("    .DataPtr   =", r.DataPtr)
                print("    .Len       =", r.Len)
                print("    .Timestamp =", timestamp)
                print("    .Flags     =", r.Flags, ",".join(flag))

            elif not next_is_indexfile:
                flag = "i" if r.Flags & MPFS2_FLAG_HASINDEX == MPFS2_FLAG_HASINDEX else "-"
                flag += "z" if r.Flags & MPFS2_FLAG_ISZIPPED == MPFS2_FLAG_ISZIPPED else "-"

                print(f"{i:4d}  {flag}  {r.Len:8d}  {timestamp}  {filename}")

            else:
                # do not display index entries if not verbose
                pass

        if not next_is_indexfile and extract:
            f = export / filename
            f.parent.mkdir(exist_ok=True, parents=True)

            if r.Flags == 1:
                # gzip'd file
                b = gzip.decompress(fs[r.DataPtr : r.DataPtr + r.Len])
                f.write_bytes(b)
            else:
                f.write_bytes(fs[r.DataPtr : r.DataPtr + r.Len])

            if verbose:
                print(f"extracted: {f.as_posix()} {r.Len} bytes")

        if r.Flags & MPFS2_FLAG_HASINDEX == MPFS2_FLAG_HASINDEX:
            next_is_indexfile = filename
        else:
            next_is_indexfile = None

    if list_variables and len(variables) > 0:
        print("Dynamic variables:")
        for num, name in variables.items():
            print(f"{num} {name}")

    if extract and len(variables) > 0:
        f = export / "DYNAMIC_VARIABLES.idx"
        f.write_text("\n".join(f"{num} {name}" for num, name in variables.items()))
        if verbose:
            print(f"created: {f.as_posix()} {len(variables)} variables")


if __name__ == "__main__":
    main()
