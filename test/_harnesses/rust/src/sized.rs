// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

// in a real program you would want this file to have an appropriate name
//   but for testing I'd rather not deal with it having a different name
//   than all the other files.
#[allow(non_snake_case)]
mod SizedMessage;
use SizedMessage::*;

mod util;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    let short_list = TextContainer {
        label: "list that fits in a byte".to_string(),
        collection: vec![
            "Lorem".to_string(), "ipsum".to_string(), "dolor".to_string(), "sit".to_string(), "amet".to_string(), "consectetur".to_string(),
            "adipiscing".to_string(), "elit".to_string(), "sed".to_string(), "do".to_string(), "eiusmod".to_string(), "tempor".to_string(),
            "incididunt".to_string(), "ut".to_string(), "labore".to_string(), "et".to_string(), "dolore".to_string(), "magna".to_string(),
            "aliqua".to_string(), "Ut".to_string(), "enim".to_string(), "ad".to_string(), "minim".to_string(), "veniam".to_string(),
            "quis".to_string(), "nostrud".to_string(), "exercitation".to_string(), "ullamco".to_string(), "laboris".to_string(), "nisi".to_string(),
            "ut".to_string(), "aliquip".to_string(), "ex".to_string(), "ea".to_string(), "commodo".to_string(), "consequat".to_string(),
            "Duis".to_string(), "aute".to_string(), "irure".to_string(), "dolor".to_string(), "in".to_string(), "reprehenderit".to_string(),
            "in".to_string(), "voluptate".to_string(), "velit".to_string(), "esse".to_string(), "cillum".to_string(), "dolore".to_string(),
            "eu".to_string(), "fugiat".to_string(), "nulla".to_string(), "pariatur".to_string(), "Excepteur".to_string(), "sint".to_string(),
            "occaecat".to_string(), "cupidatat".to_string(), "non".to_string(), "proident".to_string(), "sunt".to_string(), "in".to_string(),
            "culpa".to_string(), "qui".to_string(), "officia".to_string(), "deserunt".to_string(), "mollit".to_string(), "anim".to_string(),
            "id".to_string(), "est".to_string(), "laborum".to_string(),
        ]
    };

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();
        short_list.write_bytes(&mut writer, false);

        let filename = args.get("generate").unwrap();
        checker.soft_assert(short_list.get_size_in_bytes() == 464, "short list size calculation check");
        checker.soft_assert(writer.len() as u32 == short_list.get_size_in_bytes(), "written bytes check");
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::new(buffer);
        let input = TextContainer::from_bytes(&mut reader).unwrap();


        checker.soft_assert(input.label == short_list.label, "readback label comparison");
        checker.soft_assert(input.collection.len() == short_list.collection.len(), "readback list length");
        for i in 0..input.collection.len() {
            checker.soft_assert(input.collection[i] == short_list.collection[i], "short list comparison");
        }

    }

    checker.check();
}
