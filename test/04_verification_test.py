import beschi.writers

import test_util

writers = list(beschi.writers.all_writers.keys()) + ["swift"]

def test_basic_harness_compilation():
    for label in writers:
        test_util.build_for(label, "basic", "ComprehensiveMessage")

def test_writing_and_reading():
    for w in writers:
        test_util.run_for(w, "basic")

# checks that all generated messages from each language are byte-identical
## (because of this, we don't need to test a full matrix and can just have
##  each language read its own output)
def test_writing_comparison():
    test_util.check_files_identical("basic.*.msg")
