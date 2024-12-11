#![allow(dead_code)] // some generated functions chains may not be fully exploited

use std::fmt;
use std::error::Error;

#[derive(Debug)]
pub enum BeschiError {
    EndOfFile,
    InvalidData,
    EndOfMessageList,
}

impl Error for BeschiError {}

impl fmt::Display for BeschiError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            BeschiError::EndOfFile => write!(f, "end of file reached prematurely"),
            BeschiError::InvalidData => write!(f, "invalid data encountered"),
            BeschiError::EndOfMessageList => write!(f, "end of message list encountered"),
        }
    }
}

pub struct BufferReader<'a> {
    buffer: &'a [u8],
    pub current_position: usize,
}

impl<'a> BufferReader<'a> {
    pub fn new(buffer: &'a [u8]) -> Self {
        BufferReader { buffer, current_position: 0 }
    }

    pub fn from_vec(buffer: Vec<u8>) -> BufferReader<'static> {
        let buffer = Box::new(buffer);
        BufferReader {
            buffer: Box::leak(buffer),
            current_position: 0,
        }
    }

    pub fn is_finished(&self) -> bool {
        self.current_position >= self.buffer.len()
    }

    pub fn has_remaining(&self, size: usize) -> bool {
        self.current_position + size <= self.buffer.len()
    }

    pub fn take_byte(&mut self) -> Result<u8, BeschiError> {
        if !self.has_remaining(1) {
            return Err(BeschiError::EndOfFile);
        }
        self.current_position += 1;
        Ok(self.buffer[self.current_position-1])
    }

    pub fn take(&mut self, amount: usize) -> Result<&[u8], BeschiError> {
        if !self.has_remaining(amount) {
            return Err(BeschiError::EndOfFile);
        }

        let ret: &[u8] = &self.buffer[self.current_position..self.current_position+amount];
        self.current_position += amount;
        Ok(ret)
    }

    pub fn read_string(&mut self) -> Result<String, BeschiError> {
        let len = self.read_{# STRING_SIZE_TYPE #}()?;
        let string_bytes = self.take(len as usize)?;
        match String::from_utf8(string_bytes.to_vec()) {
            Err(_) => Err(BeschiError::InvalidData),
            Ok(v) => Ok(v)
        }
    }

    pub fn read_u8(&mut self) -> Result<u8, BeschiError> {
        let byte = self.take_byte()?;
        Ok(byte)
    }

    pub fn read_i16(&mut self) -> Result<i16, BeschiError> {
        let bytes = self.take(2)?;
        Ok(i16::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_u16(&mut self) -> Result<u16, BeschiError> {
        let bytes = self.take(2)?;
        Ok(u16::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_i32(&mut self) -> Result<i32, BeschiError> {
        let bytes = self.take(4)?;
        Ok(i32::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_u32(&mut self) -> Result<u32, BeschiError> {
        let bytes = self.take(4)?;
        Ok(u32::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_i64(&mut self) -> Result<i64, BeschiError> {
        let bytes = self.take(8)?;
        Ok(i64::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_u64(&mut self) -> Result<u64, BeschiError> {
        let bytes = self.take(8)?;
        Ok(u64::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_f32(&mut self) -> Result<f32, BeschiError> {
        let bytes = self.take(4)?;
        Ok(f32::from_le_bytes(bytes.try_into().unwrap()))
    }

    pub fn read_f64(&mut self) -> Result<f64, BeschiError> {
        let bytes = self.take(8)?;
        Ok(f64::from_le_bytes(bytes.try_into().unwrap()))
    }
}

pub trait MessageCodec {
    fn get_message_type(&self) -> MessageType;
    fn get_size_in_bytes(&self) -> usize;
    fn from_bytes(reader: &mut BufferReader) -> Result<Self, BeschiError>
        where Self: Sized;
    fn write_bytes(&self, writer: &mut Vec<u8>, tag: bool);
}


pub fn get_packed_size(msg_list: &[Message]) -> usize {
    let mut size: usize = 0;

    for msg in msg_list {
        size += msg.get_size_in_bytes();
    }
    size += msg_list.len();
    size += 9;

    size
}

pub fn pack_messages(msg_list: &[Message], writer: &mut Vec<u8>) {
    let header_bytes = b"BSCI";
    writer.extend_from_slice(header_bytes);
    let msg_count = msg_list.len() as u32;
    writer.extend_from_slice(&msg_count.to_le_bytes());

    for msg in msg_list {
        msg.write_bytes(writer, true);
    }
    writer.push(0);
}

pub fn unpack_messages(reader: &mut BufferReader) -> Result<Vec<Message>, BeschiError> {
    let header_label = reader.take(4)?;
    if header_label != b"BSCI" {
        return Err(BeschiError::InvalidData);
    }

    let msg_count = reader.read_u32()? as usize;
    if msg_count == 0 {
        return Ok(Vec::new());
    }

    let msg_list = process_raw_bytes(reader, msg_count as i32)?;
    let read_count = msg_list.len();
    if read_count == 0 {
        return Err(BeschiError::InvalidData);
    }
    if msg_list.len() != msg_count {
        return Err(BeschiError::InvalidData);
    }

    Ok(msg_list)
}
