#!/usr/bin/env python3

import filecmp
import os
import pathlib
import shutil
import tempfile
import unittest

import mpfs2
from click.testing import CliRunner

# from https://github.com/Microchip-MPLAB-Harmony/core/blob/master/system/fs/mpfs/src/mpfs.c.ftl
# fmt: off
NVM_MEDIA_DATA = bytes([
	0x4d,0x50,0x46,0x53,0x02,0x01,0x02,0x00,0x68,0x8f,0x08,0x9f,0x38,0x00,0x00,0x00,  # MPFS....h...8...
	0x4a,0x00,0x00,0x00,0x0b,0x00,0x00,0x00,0x4a,0x3c,0xd6,0x53,0x00,0x00,0x00,0x00,  # J.......J<.S....
	0x00,0x00,0x41,0x00,0x00,0x00,0x55,0x00,0x00,0x00,0x0a,0x00,0x00,0x00,0x50,0x3c,  # ..A...U.......P<
	0xd6,0x53,0x00,0x00,0x00,0x00,0x00,0x00,0x46,0x49,0x4c,0x45,0x2e,0x74,0x78,0x74,  # .S......FILE.txt
	0x00,0x54,0x45,0x53,0x54,0x2e,0x74,0x78,0x74,0x00,0x48,0x65,0x6c,0x6c,0x6f,0x20,  # .TEST.txt.Hello
	0x57,0x6f,0x72,0x6c,0x64,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x30        # World1234567890
])
# fmt: on


class Mpfs2TestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = None
        os.chdir(pathlib.Path(__file__).parent)

    def tearDown(self):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)

    def test_help(self) -> None:
        runner = CliRunner()
        args = ["--help"]
        result = runner.invoke(mpfs2.main, args)
        exit_code = 0
        self.assertEqual(result.exit_code, exit_code)
        self.assertTrue(result.output.startswith("Usage: "))

    def test_unknown_opt(self) -> None:
        runner = CliRunner()
        args = ["--lol"]
        result = runner.invoke(mpfs2.main, args)
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(result.output.startswith("Usage: "))
        self.assertTrue("no such option" in result.output)

    def test_noarg(self) -> None:
        runner = CliRunner()
        args = []
        result = runner.invoke(mpfs2.main, args)
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(result.output.startswith("Usage: "))
        self.assertTrue("Missing argument" in result.output)

    def test_open(self) -> None:
        runner = CliRunner()
        args = ["MPFS2/out/test.bin"]
        result = runner.invoke(mpfs2.main, args)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Version: 2.1\n" in result.output)
        self.assertTrue("Number of files: 3 (" in result.output)
        self.assertTrue("Number of dynamic variables: 0\n" in result.output)

    def test_list(self) -> None:
        runner = CliRunner()
        args = ["-l", "MPFS2/out/test.bin"]
        result = runner.invoke(mpfs2.main, args)
        exit_code = 0
        self.assertEqual(result.exit_code, exit_code)
        ok = 0
        for line in result.output.split("\n"):
            v = line.split()
            if len(v) == 5:
                if v[2] == "142" and v[4] == "index.html":
                    ok = ok + 1
                if v[2] == "8" and v[4] == "data":
                    ok = ok + 100
                if v[2] == "351" and v[4] == "protect/tree.txt":
                    ok = ok + 10000
        self.assertEqual(ok, 10101)

    def test_list_verbose(self) -> None:
        runner = CliRunner()
        args = ["-l", "-v", "MPFS2/out/test.bin"]
        result = runner.invoke(mpfs2.main, args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("FileRecord 0:", result.output)
        self.assertIn("FileRecord 1:", result.output)
        self.assertIn("FileRecord 2:", result.output)
        self.assertNotIn("FileRecord 3:", result.output)

    def test_extract(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        runner = CliRunner()
        args = ["-x", "-d", self.temp_dir, "MPFS2/out/test.bin"]
        result = runner.invoke(mpfs2.main, args)
        self.assertEqual(result.exit_code, 0)
        dcmp = filecmp.dircmp("MPFS2/files", self.temp_dir)
        self.assertEqual(dcmp.diff_files, [])
        self.assertEqual(sorted(dcmp.same_files), sorted(["index.html", "data"]))
        self.assertEqual(dcmp.common_dirs, ["protect"])

    def test_extract2(self) -> None:
        tmp_mpfs2 = tempfile.NamedTemporaryFile("wb+")
        tmp_mpfs2.write(NVM_MEDIA_DATA)
        tmp_mpfs2.flush()
        runner = CliRunner()
        args = ["-l", tmp_mpfs2.name]
        result = runner.invoke(mpfs2.main, args)
        tmp_mpfs2.close()
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" FILE.txt\n", result.output)
        self.assertIn(" TEST.txt\n", result.output)


if __name__ == "__main__":
    unittest.main(module="test_mpfs2")
