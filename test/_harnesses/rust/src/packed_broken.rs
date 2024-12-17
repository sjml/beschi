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
        writer[4] = 15;

        let filename = args.get("generate").unwrap();
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::from_vec(buffer);
        match unpack_messages(&mut reader) {
            Ok(_) => checker.soft_assert(false, "broken unpack"),
            Err(e) => match e {
                small_messages::SmallMessagesError::InvalidData => {},
                _ => checker.soft_assert(false, "broken unpack error")
            }
        };
    }

    checker.check();
}
