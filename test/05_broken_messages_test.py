import os
import subprocess

import beschi.writers

import test_util

def test_broken_message_handling():
    if not os.path.exists(test_util.DATA_OUTPUT_DIR):
        os.makedirs(test_util.DATA_OUTPUT_DIR)

    for w in beschi.writers.all_writers:
        test_util.build_for(w, "broken", "BrokenMessages")
        out_file = os.path.join(test_util.DATA_OUTPUT_DIR, f"broken.{w}.msg")
        if os.path.exists(out_file):
            os.unlink(out_file)
        assert(not os.path.exists(out_file))
        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"broken_{w}"),
            "--generateBroken", out_file
        ])
        assert(os.path.exists(out_file))

        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"broken_{w}"),
            "--readBroken", out_file
        ])

def test_truncated_message_handling():
    if not os.path.exists(test_util.DATA_OUTPUT_DIR):
        os.makedirs(test_util.DATA_OUTPUT_DIR)

    for w in beschi.writers.all_writers:
        out_file = os.path.join(test_util.DATA_OUTPUT_DIR, f"truncated.{w}.msg")
        if os.path.exists(out_file):
            os.unlink(out_file)
        assert(not os.path.exists(out_file))
        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"broken_{w}"),
            "--generateTruncated", out_file
        ])
        assert(os.path.exists(out_file))

        subprocess.check_call([
            os.path.join(test_util.HARNESS_BIN_DIR, f"broken_{w}"),
            "--readTruncated", out_file
        ])


