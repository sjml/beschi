import beschi.writers

import test_util

writers = list(beschi.writers.all_writers.keys()) + ["swift"]

def test_multiple_message_handling():
    for w in writers:
        test_util.build_for(w, "multiple", "SmallMessages")
        test_util.run_for(w, "multiple")

def test_multiple_message_writing_comparison():
    test_util.check_files_identical("multiple.*.msg")

def test_multiple_message_broken_stream():
    for w in writers:
        test_util.build_for(w, "multiple_broken", "BrokenMessages")
        test_util.run_for(w, "multiple_broken")

def test_multiple_message_broken_writing_comparison():
    test_util.check_files_identical("multiple_broken.*.msg")
