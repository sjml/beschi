import os
import filecmp
import glob

import beschi.writers

import test_util

def test_multiple_message_handling():
    for w in beschi.writers.all_writers:
        test_util.build_for(w, "multiple", "SmallMessages")
        test_util.run_for(w, "multiple")

def test_multiple_message_writing_comparison():
    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(test_util.DATA_OUTPUT_DIR, "multiple.*.msg")))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        assert(filecmp.cmp(messages[i], messages[j], False))

def test_multiple_message_broken_stream():
    for w in beschi.writers.all_writers:
        test_util.build_for(w, "multiple_broken", "BrokenMessages")
        test_util.run_for(w, "multiple_broken")

def test_multiple_message_broken_writing_comparison():
    filecmp.clear_cache()
    messages = (glob.glob(os.path.join(test_util.DATA_OUTPUT_DIR, "multiple_broken.*.msg")))
    for i in range(len(messages)):
        j = i + 1
        if j >= len(messages):
            j -= len(messages)
        assert(filecmp.cmp(messages[i], messages[j], False))
