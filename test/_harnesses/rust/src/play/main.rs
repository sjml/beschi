use std::fs;
use std::fmt;

#[derive(Debug)]
pub enum BeschiError {
    EndOfFile,
    InvalidData,
}
impl fmt::Display for BeschiError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            BeschiError::EndOfFile => write!(f, "end of file reached prematurely"),
            BeschiError::InvalidData => write!(f, "invalid data encountered"),
        }
    }
}

struct BufferReader {
    buffer: Vec<u8>,
    current_position: usize,
}
impl BufferReader {
    pub fn new(buffer: Vec<u8>) -> Self {
        BufferReader { buffer, current_position: 0 }
    }

    pub fn is_finished(self) -> bool {
        if self.current_position >= self.buffer.len() {
            return true
        }
        false
    }

    pub fn has_remaining(self, size: usize) -> bool {
        if self.current_position + size >= self.buffer.len() {
            return false
        }
        true
    }

    pub fn take(&mut self, amount: usize) -> Result<&[u8], BeschiError> {
        if amount + self.current_position > self.buffer.len() {
            return Err(BeschiError::EndOfFile);
        }

        let ret: &[u8] = &self.buffer
            [self.current_position..self.current_position+amount];
        self.current_position += amount;
        println!("taking {} bytes, new offset is {}", amount, self.current_position);
        Ok(ret)
    }
}

#[derive(Default)]
struct Vec2 {
    x: f32,
    y: f32,
}
impl Vec2 {
    pub fn from_bytes(reader: &mut BufferReader) -> Result<Vec2, BeschiError> {
        let xbytes = reader.take(4)?;
        let x = f32::from_le_bytes(xbytes.try_into().unwrap());
        let ybytes = reader.take(4)?;
        let y = f32::from_le_bytes(ybytes.try_into().unwrap());

        Ok(Vec2 {x, y})
    }
}

fn main() {
        let filename = "../../../out/data/broken.c.msg";
        let buffer = fs::read(&filename).unwrap();

        let mut reader = BufferReader::new(buffer);

        // would let this error propagate to the caller in larger context
        let v2 = match Vec2::from_bytes(&mut reader) {
            Err(_) => {
                println!("couldn't read buffer for some reason! :(");
                Vec2 { x: -1.0, y: -1.0 }
            },
            Ok(v) => v
        };
        println!("{{ x: {:.1}, y: {:.1} }}", v2.x, v2.y);
}
