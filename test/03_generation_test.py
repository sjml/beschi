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
    test_util.generate_for("./test/_protocols/example.toml", "ComprehensiveMessage")

def test_basic_harness_compilation():
    if not os.path.exists(test_util.HARNESS_BIN_DIR):
        os.makedirs(test_util.HARNESS_BIN_DIR)
    for label, writer in beschi.writers.all_writers.items():
        harness_path = os.path.join(test_util.HARNESS_SRC_DIR, label)
        invoke_build = [
            "python", f"{harness_path}/builder.py",
            "--srcfile", f"basic{writer.default_extension}",
            "--libfile", f"ComprehensiveMessage{writer.default_extension}",
        ]
        subprocess.check_call(invoke_build + ["--clean"])
        subprocess.check_call(invoke_build)

