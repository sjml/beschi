
use std::fs;
use std::fmt;
use std::convert::TryInto;

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

#[derive(Default)]
struct Vec3 {
    x: f32,
    y: f32,
    z: f32,
}

fn get_vec3(buffer: &[u8]) -> Result<Vec3, BeschiError> {
    if buffer.len() < 12 {
        return Err(BeschiError::EndOfFile);
    }

    Ok(Vec3 {
        x: f32::from_le_bytes((&buffer[0..4]).try_into().unwrap()),
        y: f32::from_le_bytes((&buffer[4..8]).try_into().unwrap()),
        z: 0.0,
    })
}

fn main() {
    let filename = "../../../out/data/broken.c.msg";
    let buffer = fs::read(&filename).unwrap();
    println!("buffer length: {}", buffer.len());

    let v3 = match get_vec3(&buffer) {
        Ok(v) => v,
        // would probably want this to propogate and let the message reader return null,
        //   but just playing at the moment
        Err(_) => Vec3 { x: -1.0, y: -1.0, z: -1.0 }
    };

    println!("x: {}, y: {}, z: {}", v3.x, v3.y, v3.z);

    let v32 = get_vec3(&buffer);
    if v32.is_err() {
        println!("Couldn't fully read buffer from {}", filename);
    }

}
