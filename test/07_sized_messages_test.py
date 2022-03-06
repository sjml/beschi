import test_util

def test_sized_lists_and_string_handling(generator_label):
    test_util.build_for(generator_label, "sized", ["SizedMessage"])
    test_util.run_for(generator_label, "sized")

def test_sized_lists_and_string_writing_comparison():
    test_util.check_files_identical("sized.*.msg")
