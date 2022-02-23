import pytest

from beschi.protocol import Protocol

def test_good_protocol():
    p = Protocol("test/_protocols/example.toml")

def test_empty_protocol():
    p = Protocol("test/_protocols/empty.toml")

def test_protocol_not_exist():
    with pytest.raises(FileNotFoundError):
        p = Protocol("test/_protocols/nope.toml")

def test_protocol_oversize():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/oversize.toml")

def test_protocol_whitespace_in_namespace():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/whitespace_in_namespace.toml")

def test_protocol_whitespace_in_struct_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/whitespace_in_struct_name.toml")

def test_protocol_whitespace_in_message_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/whitespace_in_message_name.toml")

def test_protocol_whitespace_in_variable_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/whitespace_in_variable_name.toml")

def test_protocol_bad_type_on_message():
    with pytest.raises(NotImplementedError):
        p = Protocol("test/_protocols/intentionally_bad/bad_type_on_message.toml")

def test_protocol_bad_type_on_struct():
    with pytest.raises(NotImplementedError):
        p = Protocol("test/_protocols/intentionally_bad/bad_type_on_struct.toml")

def test_protocol_duplicate_message_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/duplicate_message_name.toml")

def test_protocol_duplicate_struct_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/duplicate_struct_name.toml")

def test_protocol_missing_message_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/missing_message_name.toml")

def test_protocol_missing_struct_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/missing_struct_name.toml")

def test_protocol_reserved_struct_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/reserved_name_on_struct.toml")

def test_protocol_reserved_message_name():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/reserved_name_on_message.toml")

def test_protocol_message_duplicating_struct():
    with pytest.raises(ValueError):
        p = Protocol("test/_protocols/intentionally_bad/message_duplicating_struct_name.toml")
