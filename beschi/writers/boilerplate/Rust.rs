use std::fmt;
use std::error::Error;

#[derive(Debug)]
pub enum BeschiError {
    EndOfFile,
    InvalidData,
}

impl Error for BeschiError {}

impl fmt::Display for BeschiError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            BeschiError::EndOfFile => write!(f, "end of file reached prematurely"),
            BeschiError::InvalidData => write!(f, "invalid data encountered"),
        }
    }
}

pub struct BufferReader {
    buffer: Vec<u8>,
    current_position: usize,
}

impl BufferReader {
    pub fn new(buffer: Vec<u8>) -> Self {
        BufferReader { buffer, current_position: 0 }
    }

    pub fn is_finished(&self) -> bool {
        if self.current_position >= self.buffer.len() {
            return true
        }
        false
    }

    pub fn has_remaining(&self, size: usize) -> bool {
        if self.current_position + size > self.buffer.len() {
            return false
        }
        true
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

