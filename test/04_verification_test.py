import os
import subprocess
import filecmp
import glob

import beschi.writers

import test_util


def test_basic_harness_compilation():
    for label in beschi.writers.all_writers:
        test_util.build_for(label, "basic", "ComprehensiveMessage")

def test_writing():
    if not os.path.exists(test_util.DATA_OUTPUT_DIR):
        os.makedirs(test_util.DATA_OUTPUT_DIR)
    for w in beschi.writers.all_writers:
        out_file = os.path.join(test_util.DATA_OUTPUT_DIR, f"basic.{w}.msg")
        if os.path.exists(out_file):
            os.unlink(out_file)
        assert(not os.path.exists(out_file))
        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"basic_{w}"),
            "--generate", out_file
        ])
        assert(os.path.exists(out_file))

# checks that all generated messages from each language are byte-identical
def test_writing_comparison():
    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(test_util.DATA_OUTPUT_DIR, "*.msg")))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        assert(filecmp.cmp(messages[i], messages[j], False))

# since we've already shown that all the generated messages are identical,
#   we just need to have each one read it's own instead of doing a matrix
def test_reading():
    for w in beschi.writers.all_writers:
        out_file = os.path.join(test_util.DATA_OUTPUT_DIR, f"basic.{w}.msg")
        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"basic_{w}"),
            "--read", out_file
        ])
