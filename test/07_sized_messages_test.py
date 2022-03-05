import test_util

def test_multiple_message_handling(generator_label):
    test_util.build_for(generator_label, "sized", "SizedMessage")
    test_util.run_for(generator_label, "sized")
