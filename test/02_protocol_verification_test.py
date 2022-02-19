import pytest

from beschi.protocol import Protocol

import test_util

# should not raise an exception
def test_good_protocol():
    p = Protocol("test/_protocols/example.toml")

def test_protocol_not_exist():
    with pytest.raises(FileNotFoundError):
        p = Protocol("test/_protocols/nope.toml")

def test_protocol_oversize():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/oversize.toml")

# namespace, if exists, should not contain spaces
# missing name on struct/message
# duplicate name on struct/message
# bad type on struct/message
