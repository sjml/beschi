// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

mod small_messages;
use small_messages::*;

mod util;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    let msg_list = vec![
        Message::IntMessage(IntMessage::default()),
        Message::FloatMessage(FloatMessage::default()),
        Message::FloatMessage(FloatMessage::default()),
        Message::FloatMessage(FloatMessage::default()),
        Message::IntMessage(IntMessage::default()),
        Message::EmptyMessage(EmptyMessage::default()),
        Message::LongMessage(LongMessage::default()),
        Message::LongMessage(LongMessage::default()),
        Message::LongMessage(LongMessage::default()),
        Message::IntMessage(IntMessage::default()),
    ];

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();

        pack_messages(&msg_list, &mut writer);

        let filename = args.get("generate").unwrap();
        checker.soft_assert(writer.len() == 67, "size calculation check");
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::new(buffer);
        let msg_list = unpack_messages(&mut reader).unwrap();
        checker.soft_assert(msg_list.len() == 10, "packed count");

        match &msg_list[0] {
            small_messages::Message::IntMessage(_) => {},
            _ => checker.soft_assert(false, "packed[0]"),
        }
        match &msg_list[1] {
            small_messages::Message::FloatMessage(_) => {},
            _ => checker.soft_assert(false, "packed[1]"),
        }
        match &msg_list[2] {
            small_messages::Message::FloatMessage(_) => {},
            _ => checker.soft_assert(false, "packed[2]"),
        }
        match &msg_list[3] {
            small_messages::Message::FloatMessage(_) => {},
            _ => checker.soft_assert(false, "packed[3]"),
        }
        match &msg_list[4] {
            small_messages::Message::IntMessage(_) => {},
            _ => checker.soft_assert(false, "packed[4]"),
        }
        match &msg_list[5] {
            small_messages::Message::EmptyMessage(_) => {},
            _ => checker.soft_assert(false, "packed[5]"),
        }
        match &msg_list[6] {
            small_messages::Message::LongMessage(_) => {},
            _ => checker.soft_assert(false, "packed[6]"),
        }
        match &msg_list[7] {
            small_messages::Message::LongMessage(_) => {},
            _ => checker.soft_assert(false, "packed[7]"),
        }
        match &msg_list[8] {
            small_messages::Message::LongMessage(_) => {},
            _ => checker.soft_assert(false, "packed[8]"),
        }
        match &msg_list[9] {
            small_messages::Message::IntMessage(_) => {},
            _ => checker.soft_assert(false, "packed[9]"),
        }

    }

    checker.check();
}
