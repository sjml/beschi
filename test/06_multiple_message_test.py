import test_util

def test_multiple_message_handling(generator_label):
    test_util.build_for(generator_label, "multiple", "SmallMessages")
    test_util.run_for(generator_label, "multiple")

def test_multiple_message_writing_comparison():
    test_util.check_files_identical("multiple.*.msg")

def test_multiple_message_broken_stream(generator_label):
    test_util.build_for(generator_label, "multiple_broken", "BrokenMessages")
    test_util.run_for(generator_label, "multiple_broken")

def test_multiple_message_broken_writing_comparison():
    test_util.check_files_identical("multiple_broken.*.msg")
