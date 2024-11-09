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

def test_protocol_list_of_lists():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/list_of_lists.toml")

def test_protocol_enum_missing_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_missing_name.toml")

def test_protocol_enum_whitespace_in_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_whitespace_in_name.toml")

def test_protocol_enum_reserved_name():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_reserved_name.toml")

def test_protocol_enum_missing_values():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_missing_values.toml")

def test_protocol_enum_empty_values():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_empty_values.toml")

def test_protocol_enum_non_string_values():
    with pytest.raises(TypeError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_non_string_values.toml")

def test_protocol_enum_duplicate_values_names():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_duplicate_values_names.toml")

def test_protocol_enum_duplicate_values_numbers():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_duplicate_values_numbers.toml")

def test_protocol_enum_value_shadows_struct():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_shadows_struct.toml")

def test_protocol_enum_value_shadows_message():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_shadows_message.toml")

def test_protocol_enum_value_subtable_missing_name():
    with pytest.raises(TypeError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_subtable_missing_name.toml")

def test_protocol_enum_value_subtable_missing_value():
    with pytest.raises(TypeError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_subtable_missing_value.toml")

def test_protocol_enum_value_subtable_wrong_type_name():
    with pytest.raises(TypeError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_subtable_wrong_type_name.toml")

def test_protocol_enum_value_subtable_wrong_type_value():
    with pytest.raises(TypeError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_subtable_wrong_type_value.toml")

def test_protocol_enum_value_number_out_of_range_high():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_number_out_of_range_high.toml")

def test_protocol_enum_value_number_out_of_range_low():
    with pytest.raises(ValueError):
        _ = Protocol("test/_protocols/intentionally_bad/enum_value_number_out_of_range_low.toml")

def test_protocol_enum_i16_values():
    p = Protocol("test/_protocols/enum_256.toml")
    assert(len(p.enums) == 1)
    assert(next(iter(p.enums.items()))[1].encoding == "int16")

def test_protocol_enum_i32_values():
    p = Protocol("test/_protocols/enum_32768.toml")
    assert(len(p.enums) == 1)
    assert(next(iter(p.enums.items()))[1].encoding == "int32")

## actually testing the int32 limit would involve a 15 GB protocol file, so no.
##   (when limiting the possible types to just byte and int16, the last test
##   here properly failed, so gonna just say the int32 one would also.)
