import test_util

def test_basic_harness_compilation(generator_label):
    test_util.build_for(generator_label, "basic", ["ComprehensiveMessage"])

def test_writing_and_reading(generator_label):
    test_util.run_for(generator_label, "basic")

# checks that all generated messages from each language are byte-identical
## (because of this, we don't need to test a full matrix and can just have
##  each language read its own output)
def test_writing_comparison():
    test_util.check_files_identical("basic.*.msg")
