import beschi.writers

import test_util

def test_broken_message_handling():
    for w in beschi.writers.all_writers:
        test_util.build_for(w, "broken", "BrokenMessages")
        test_util.run_for(w, "broken")

def test_truncated_message_handling():
    for w in beschi.writers.all_writers:
        test_util.build_for(w, "truncated", "BrokenMessages")
        test_util.run_for(w, "truncated")


