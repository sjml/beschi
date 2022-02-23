import beschi.writers

import test_util

writers = list(beschi.writers.all_writers.keys())

def test_broken_message_handling():
    for w in writers:
        test_util.build_for(w, "broken", "BrokenMessages")
        test_util.run_for(w, "broken")
        test_util.check_files_identical("broken.*.msg")

def test_truncated_message_handling():
    for w in writers:
        test_util.build_for(w, "truncated", "BrokenMessages")
        test_util.run_for(w, "truncated")
        test_util.check_files_identical("truncated.*.msg")


