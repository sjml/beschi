// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

// in a real program you would want this file to have an appropriate name
//   but for testing I'd rather not deal with it having a different name
//   than all the other files.
#[allow(non_snake_case)]
mod BrokenMessages;
use BrokenMessages::*;

mod util;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    let lmsg = BrokenMessages::ListMessage { ints: vec![1, 2, 32767, 4, 5] };

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();
        lmsg.write_bytes(&mut writer, false);

        // tweak the buffer so the message looks longer
        writer[0] = 0xFF;

        let filename = args.get("generate").unwrap();
        checker.soft_assert(writer.len() == 14, "size calculation check");
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::new(buffer);
        let read_res = ListMessage::from_bytes(&mut reader);
        match read_res {
            Ok(_) => checker.soft_assert(false, "reading truncated message"),
            Err(_) => checker.soft_assert(true, "reading truncated message")
        }
    }

    checker.check();
}
