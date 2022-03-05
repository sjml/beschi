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

    let trunc = BrokenMessages::TruncatedMessage { x: 1.0, y: 2.0 };
    let full = BrokenMessages::FullMessage { x: 1.0, y: 2.0, z: 3.0 };

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();

        full.write_bytes(&mut writer, true);
        full.write_bytes(&mut writer, true);
        full.write_bytes(&mut writer, true);

        // write a truncated message tagged as a full one
        writer.push(1_u8);
        trunc.write_bytes(&mut writer, false);

        full.write_bytes(&mut writer, true);
        full.write_bytes(&mut writer, true);
        full.write_bytes(&mut writer, true);

        let mut size = 0;
        size += 6 * full.get_size_in_bytes();
        size += 6; // markers
        size += trunc.get_size_in_bytes();
        size += 1; // trunc marker

        let filename = args.get("generate").unwrap();
        checker.soft_assert(writer.len() as u32 == size, "size calculation check");
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::new(buffer);
        match BrokenMessages::process_raw_bytes(&mut reader) {
            Err(_) => checker.soft_assert(true, "read broken stream length"),
            Ok(_) => checker.soft_assert(false, "read broken stream length"),
        }
    }

    checker.check();
}
