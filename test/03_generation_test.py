import os
import shutil
import subprocess

import beschi.writers

import test_util

# see if the executable version works
def test_cli_exists():
    assert(shutil.which("beschi") != None)

# generate each given file for the example protocol
def test_generation():
    for label, writer_class in beschi.writers.all_writers.items():
        out_file_dir =  os.path.join(test_util.CODE_OUTPUT_DIR, label)
        out_file_path = os.path.join(out_file_dir, f"WireMessage{writer_class.default_extension}")

        if os.path.exists(out_file_path):
            os.unlink(out_file_path)
        assert(not os.path.exists(out_file_path))

        if not os.path.exists(out_file_dir):
            os.makedirs(out_file_dir)

        subprocess.check_call(["beschi",
            "--lang", label,
            "--protocol", "./test/_protocols/example.toml",
            "--output", out_file_path
        ])
        assert(os.path.exists(out_file_path))

def test_harness_compilation():
    if not os.path.exists(test_util.HARNESS_BIN_DIR):
        os.makedirs(test_util.HARNESS_BIN_DIR)
    for label in beschi.writers.all_writers:
        harness_path = os.path.join(test_util.HARNESS_SRC_DIR, label)
        curr_dir = os.getcwd()
        os.chdir(harness_path)
        subprocess.check_call(["make", "clean"])
        subprocess.check_call(["make"])
        os.chdir(curr_dir)

