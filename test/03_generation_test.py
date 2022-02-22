import shutil

import test_util

# see if the executable version works
def test_cli_exists():
    assert(shutil.which("beschi") != None)

# generate each given file for the example protocol
def test_generation():
    test_util.generate_for("./test/_protocols/empty.toml", "Empty")
    test_util.generate_for("./test/_protocols/example.toml", "ComprehensiveMessage")
    test_util.generate_for("./test/_protocols/broken_messages.toml", "BrokenMessages")
    test_util.generate_for("./test/_protocols/small_messages.toml", "SmallMessages")
    test_util.generate_for("./test/_protocols/annotated.toml", "AppMessages")

