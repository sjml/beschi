import test_util

def test_uninitialized_message(generator_label):
    test_util.build_for(generator_label, "uninitialized", ["ComprehensiveMessage"])
    test_util.run_for(generator_label, "uninitialized")

def test_uninitialized_message_writing_comparison():
    test_util.check_files_identical("uninitialized.*.msg")
