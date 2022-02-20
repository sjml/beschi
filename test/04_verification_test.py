import os
import subprocess
import filecmp
import glob

import beschi.writers

import test_util


def test_basic_harness_compilation():
    for label in beschi.writers.all_writers:
        test_util.build_for(label, "basic", "ComprehensiveMessage")

def test_writing_and_reading():
    for w in beschi.writers.all_writers:
        test_util.run_for(w, "basic")

# checks that all generated messages from each language are byte-identical
## (because of this, we don't need to test a full matrix and can just have
##  each language read its own output)
def test_writing_comparison():
    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(test_util.DATA_OUTPUT_DIR, "basic.*.msg")))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        assert(filecmp.cmp(messages[i], messages[j], False))
