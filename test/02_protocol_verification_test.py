import pytest

from beschi.protocol import Protocol

def test_good_protocol():
    _ = Protocol("test/_protocols/example.toml")

def test_empty_protocol():
    _ = Protocol("test/_protocols/empty.toml")

def test_protocol_not_exist():
    with pytest.raises(FileNotFoundError):
        _ = Protocol("test/_protocols/nope.toml")

def test_protocol_oversize():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/oversize.toml")

def test_protocol_whitespace_in_namespace():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/whitespace_in_namespace.toml")

def test_protocol_whitespace_in_struct_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/whitespace_in_struct_name.toml")

def test_protocol_whitespace_in_message_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/whitespace_in_message_name.toml")

def test_protocol_whitespace_in_variable_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/whitespace_in_variable_name.toml")

def test_protocol_bad_type_on_message():
    with pytest.raises(NotImplementedError):
        _ = Protocol("test/_protocols/intentionally_bad/bad_type_on_message.toml")

def test_protocol_bad_type_on_struct():
    with pytest.raises(NotImplementedError):
        _ = Protocol("test/_protocols/intentionally_bad/bad_type_on_struct.toml")

def test_protocol_duplicate_message_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/duplicate_message_name.toml")

def test_protocol_duplicate_struct_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/duplicate_struct_name.toml")

def test_protocol_missing_message_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/missing_message_name.toml")

def test_protocol_missing_struct_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/missing_struct_name.toml")

def test_protocol_reserved_struct_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/reserved_name_on_struct.toml")

def test_protocol_reserved_message_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/reserved_name_on_message.toml")

def test_protocol_message_duplicating_struct():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/message_duplicating_struct_name.toml")

def test_protocol_infinite_loop():
    with pytest.raises(RecursionError):
        _ = Protocol("test/_protocols/intentionally_bad/simple_infinite_loop.toml")

def test_protocol_deep_infinite_loop():
    with pytest.raises(RecursionError):
        _ = Protocol("test/_protocols/intentionally_bad/deep_infinite_loop.toml")

def test_protocol_message_containing_message():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/message_containing_message.toml")

def test_protocol_size_values():
    _ = Protocol("test/_protocols/sized.toml")
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/bad_list_size_val.toml")
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/bad_string_size_val.toml")
