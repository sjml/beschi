// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

mod small_messages;

mod util;

use small_messages::MessageCodec;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    let empty_msg = small_messages::EmptyMessage {};
    let byte_msg = small_messages::ByteMessage { byte_member: 242 };
    let int_msg_a = small_messages::IntMessage { int_member: -42 };
    let int_msg_b = small_messages::IntMessage { int_member: 2048 };
    let float_msg = small_messages::FloatMessage { float_member: 1234.5678 };
    let long_msg = small_messages::LongMessage { int_member: 2147483647 + 10 };

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();

        byte_msg.write_bytes(&mut writer, true);   //  0
        int_msg_a.write_bytes(&mut writer, true);  //  1
        int_msg_b.write_bytes(&mut writer, true);  //  2
        empty_msg.write_bytes(&mut writer, true);  //  3
        long_msg.write_bytes(&mut writer, true);   //  4
        float_msg.write_bytes(&mut writer, true);  //  5
        int_msg_a.write_bytes(&mut writer, true);  //  6
        int_msg_b.write_bytes(&mut writer, true);  //  7
        int_msg_b.write_bytes(&mut writer, true);  //  8
        int_msg_b.write_bytes(&mut writer, true);  //  9
        int_msg_a.write_bytes(&mut writer, true);  // 10
        empty_msg.write_bytes(&mut writer, true);  // 11

        let mut size = 0;
        size += byte_msg.get_size_in_bytes();
        size += int_msg_a.get_size_in_bytes() * 3;
        size += int_msg_b.get_size_in_bytes() * 4;
        size += empty_msg.get_size_in_bytes() * 2;
        size += long_msg.get_size_in_bytes();
        size += float_msg.get_size_in_bytes();
        size += 12;

        let filename = args.get("generate").unwrap();
        checker.soft_assert(writer.len() == size, "size calculation check");
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let mut buffer = fs::read(&filename).unwrap();
        buffer.resize(buffer.len() + 25, 0);
        let mut reader = small_messages::BufferReader::new(buffer);
        let msg_list = small_messages::process_raw_bytes(&mut reader, -1).unwrap();
        checker.soft_assert(msg_list.len() == 12, "reading multiple messages length");

        match &msg_list[0] {
            small_messages::Message::ByteMessage(bm) => checker.soft_assert(bm.byte_member == byte_msg.byte_member, "msg 0 content"),
            _ => checker.soft_assert(false, "msg 0 type"),
        }
        match &msg_list[1] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_a.int_member, "msg 1 content"),
            _ => checker.soft_assert(false, "msg 1 type"),
        }
        match &msg_list[2] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_b.int_member, "msg 2 content"),
            _ => checker.soft_assert(false, "msg 2 type"),
        }
        match &msg_list[3] {
            small_messages::Message::EmptyMessage(_em) => {},
            _ => checker.soft_assert(false, "msg 3 type"),
        }
        match &msg_list[4] {
            small_messages::Message::LongMessage(lm) => checker.soft_assert(lm.int_member == long_msg.int_member, "msg 4 content"),
            _ => checker.soft_assert(false, "msg 4 type"),
        }
        match &msg_list[5] {
            small_messages::Message::FloatMessage(fm) => checker.soft_assert(fm.float_member == float_msg.float_member, "msg 5 content"),
            _ => checker.soft_assert(false, "msg 5 type"),
        }
        match &msg_list[6] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_a.int_member, "msg 6 content"),
            _ => checker.soft_assert(false, "msg 6 type"),
        }
        match &msg_list[7] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_b.int_member, "msg 7 content"),
            _ => checker.soft_assert(false, "msg 7 type"),
        }
        match &msg_list[8] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_b.int_member, "msg 8 content"),
            _ => checker.soft_assert(false, "msg 8 type"),
        }
        match &msg_list[9] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_b.int_member, "msg 9 content"),
            _ => checker.soft_assert(false, "msg 9 type"),
        }
        match &msg_list[10] {
            small_messages::Message::IntMessage(im) => checker.soft_assert(im.int_member == int_msg_a.int_member, "msg 9 content"),
            _ => checker.soft_assert(false, "msg 9 type"),
        }
        match &msg_list[11] {
            small_messages::Message::EmptyMessage(_em) => {},
            _ => checker.soft_assert(false, "msg 11 type"),
        }
    }

    checker.check();
}
