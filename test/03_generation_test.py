import pytest

import test_util

PROTOCOLS_OUTPUTS = [
    ("./test/_protocols/empty.toml", "Empty"),
    ("./test/_protocols/example.toml", "ComprehensiveMessage"),
    ("./test/_protocols/broken_messages.toml", "BrokenMessages"),
    ("./test/_protocols/small_messages.toml", "SmallMessages"),
    ("./test/_protocols/annotated.toml", "AppMessages"),
    ("./test/_protocols/sized.toml", "SizedMessage"),
]

# generate each given file for the example protocol
@pytest.mark.parametrize("protocol_output_pair", PROTOCOLS_OUTPUTS)
def test_generation(protocol_output_pair, generator_label):
    test_util.generate_for(protocol_output_pair[0], protocol_output_pair[1], generator_label)

