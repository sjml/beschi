import test_util

def test_broken_message_handling(generator_label):
    test_util.build_for(generator_label, "broken", ["BrokenMessages"])
    test_util.run_for(generator_label, "broken")

def test_broken_writing_comparison():
    test_util.check_files_identical("broken.*.msg")

def test_truncated_message_handling(generator_label):
    test_util.build_for(generator_label, "truncated", ["BrokenMessages"])
    test_util.run_for(generator_label, "truncated")

def test_truncated_writing_comparison():
    test_util.check_files_identical("truncated.*.msg")


