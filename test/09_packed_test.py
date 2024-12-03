import test_util

def test_packed_message(generator_label):
    test_util.build_for(generator_label, "packed", ["SmallMessages"])
    test_util.run_for(generator_label, "packed")

def test_packed_message_writing_comparison():
    test_util.check_files_identical("packed.*.msg")
