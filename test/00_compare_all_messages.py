# only run as part of the continuous integration test
#   since each one runs in a separate job and generates
#   its messages without the others to look at

from test_util import check_files_identical


def test_message_comparison():
    check_files_identical("*/basic.*.msg")
    check_files_identical("*/broken.*.msg")
    check_files_identical("*/truncated.*.msg")
    check_files_identical("*/multiple.*.msg")
    check_files_identical("*/multiple_broken.*.msg")
    check_files_identical("*/sized.*.msg")
    check_files_identical("*/uninitialized.*.msg")
    check_files_identical("*/packed.*.msg")


