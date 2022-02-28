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

    // pub fn rewind(&mut self) {
    //     self.current_position = 0;
    // }

    // pub fn is_finished(self) -> bool {
    //     if self.current_position >= self.buffer.len() {
    //         return true
    //     }
    //     false
    // }

    // pub fn has_remaining(self, size: usize) -> bool {
    //     if self.current_position + size >= self.buffer.len() {
    //         return false
    //     }
    //     true
    // }

    pub fn take(&mut self, amount: usize) -> Result<&[u8], BeschiError> {
        if amount + self.current_position > self.buffer.len() {
            return Err(BeschiError::EndOfFile);
        }

        let ret: &[u8] = &self.buffer[self.current_position..self.current_position+amount];
        self.current_position += amount;
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
    pub fn write_bytes(self, buffer: &mut Vec<u8>) {
        buffer.extend(self.x.to_le_bytes());
        buffer.extend(self.y.to_le_bytes());
    }
}

#[derive(Default)]
struct Vec3 {
    x: f32,
    y: f32,
    z: f32,
}
impl Vec3 {
    pub fn from_bytes(reader: &mut BufferReader) -> Result<Vec3, BeschiError> {
        let xbytes = reader.take(4)?;
        let x = f32::from_le_bytes(xbytes.try_into().unwrap());
        let ybytes = reader.take(4)?;
        let y = f32::from_le_bytes(ybytes.try_into().unwrap());
        let zbytes = reader.take(4)?;
        let z = f32::from_le_bytes(zbytes.try_into().unwrap());

        Ok(Vec3 {x, y, z})
    }
}

#[derive(Default)]
struct Color {
    r: u8,
    g: u8,
    b: u8,
}
impl Color {
    pub fn from_bytes(reader: &mut BufferReader) -> Result<Color, BeschiError> {
        let cbytes = reader.take(3)?;
        let r = cbytes[0];
        let g = cbytes[1];
        let b = cbytes[2];

        Ok(Color {r, g, b})
    }
}

#[derive(Default)]
struct ComplexData {
    identifier: u8,
    label: String,
    text_color: Color,
    background_color: Color,
    spectrum: Vec<Color>,
}
impl ComplexData {
    pub fn from_bytes(reader: &mut BufferReader) -> Result<ComplexData, BeschiError> {
        let identifierbytes = reader.take(1)?;
        let identifier = identifierbytes[0];
        let labellenbytes = reader.take(4)?;
        let labellen = u32::from_le_bytes(labellenbytes.try_into().unwrap());
        let labelbytes = reader.take(labellen as usize)?;
        let label = match String::from_utf8(labelbytes.to_vec()) {
            Err(_) => return Err(BeschiError::InvalidData),
            Ok(v) => v
        };
        let text_color = Color::from_bytes(reader)?;
        let background_color = Color::from_bytes(reader)?;
        let spectrumlenbytes = reader.take(4)?;
        let spectrumlen = u32::from_le_bytes(spectrumlenbytes.try_into().unwrap());
        let mut spectrum: Vec<Color> = Vec::new();
        for _ in 0..spectrumlen {
            spectrum.push(Color::from_bytes(reader)?);
        }

        Ok(ComplexData {
            identifier,
            label,
            text_color,
            background_color,
            spectrum,
        })
    }
}

#[derive(Default)]
struct TestingMessage {
    b: u8,
    tf: bool,
    i16: i16,
    ui16: u16,
    i32: i32,
    ui32: u32,
    i64: i64,
    ui64: u64,
    f: f32,
    d: f64,
    s: String,
    v2: Vec2,
    v3: Vec3,
    c: Color,
    sl: Vec<String>,
    v2l: Vec<Vec2>,
    v3l: Vec<Vec3>,
    cl: Vec<Color>,
    cx: ComplexData,
    cxl: Vec<ComplexData>,
}
impl TestingMessage {
    pub fn from_bytes(reader: &mut BufferReader) -> Result<TestingMessage, BeschiError> {
        let mut ret: TestingMessage = Default::default();

        let bbytes = reader.take(1)?;
        ret.b = bbytes[0];
        let tfbytes = reader.take(1)?;
        ret.tf = tfbytes[0] > 0;
        let i16bytes = reader.take(2)?;
        ret.i16 = i16::from_le_bytes(i16bytes.try_into().unwrap());
        let ui16bytes = reader.take(2)?;
        ret.ui16 = u16::from_le_bytes(ui16bytes.try_into().unwrap());
        let i32bytes = reader.take(4)?;
        ret.i32 = i32::from_le_bytes(i32bytes.try_into().unwrap());
        let ui32bytes = reader.take(4)?;
        ret.ui32 = u32::from_le_bytes(ui32bytes.try_into().unwrap());
        let i64bytes = reader.take(8)?;
        ret.i64 = i64::from_le_bytes(i64bytes.try_into().unwrap());
        let ui64bytes = reader.take(8)?;
        ret.ui64 = u64::from_le_bytes(ui64bytes.try_into().unwrap());
        let fbytes = reader.take(4)?;
        ret.f = f32::from_le_bytes(fbytes.try_into().unwrap());
        let dbytes = reader.take(8)?;
        ret.d = f64::from_le_bytes(dbytes.try_into().unwrap());
        let slenbytes = reader.take(4)?;
        let slen = u32::from_le_bytes(slenbytes.try_into().unwrap());
        let sbytes = reader.take(slen as usize)?;
        ret.s = match String::from_utf8(sbytes.to_vec()) {
            Err(_) => return Err(BeschiError::InvalidData),
            Ok(v) => v
        };
        ret.v2 = Vec2::from_bytes(reader)?;
        ret.v3 = Vec3::from_bytes(reader)?;
        ret.c = Color::from_bytes(reader)?;
        let sllenbytes = reader.take(4)?;
        let sllen = u32::from_le_bytes(sllenbytes.try_into().unwrap());
        for _ in 0..sllen {
            let slenbytes = reader.take(4)?;
            let slen = u32::from_le_bytes(slenbytes.try_into().unwrap());
            let sbytes = reader.take(slen as usize)?;
            let s = match String::from_utf8(sbytes.to_vec()) {
                Err(_) => return Err(BeschiError::InvalidData),
                Ok(v) => v
            };
            ret.sl.push(s);
        }
        let v2llenbytes = reader.take(4)?;
        let v2llen = u32::from_le_bytes(v2llenbytes.try_into().unwrap());
        for _ in 0..v2llen {
            ret.v2l.push(Vec2::from_bytes(reader)?);
        }
        let v3llenbytes = reader.take(4)?;
        let v3llen = u32::from_le_bytes(v3llenbytes.try_into().unwrap());
        for _ in 0..v3llen {
            ret.v3l.push(Vec3::from_bytes(reader)?);
        }
        let cllenbytes = reader.take(4)?;
        let cllen = u32::from_le_bytes(cllenbytes.try_into().unwrap());
        for _ in 0..cllen {
            ret.cl.push(Color::from_bytes(reader)?);
        }
        ret.cx = ComplexData::from_bytes(reader)?;
        let cxllenbytes = reader.take(4)?;
        let cxllen = u32::from_le_bytes(cxllenbytes.try_into().unwrap());
        for _ in 0..cxllen {
            ret.cxl.push(ComplexData::from_bytes(reader)?);
        }
        Ok(ret)
    }

}
impl std::fmt::Display for TestingMessage {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        writeln!(f, "b: {}", self.b)?;
        writeln!(f, "tf: {}", self.tf)?;
        writeln!(f, "i16: {}", self.i16)?;
        writeln!(f, "ui16: {}", self.ui16)?;
        writeln!(f, "i32: {}", self.i32)?;
        writeln!(f, "ui32: {}", self.ui32)?;
        writeln!(f, "i64: {}", self.i64)?;
        writeln!(f, "ui64: {}", self.ui64)?;
        writeln!(f, "f: {}", self.f)?;
        writeln!(f, "d: {}", self.d)?;
        writeln!(f, "s: {}", self.s)?;
        writeln!(f, "v2: {{ x: {:.1}, y: {:.1} }}", self.v2.x, self.v2.y)?;
        writeln!(f, "v3: {{ x: {:.1}, y: {:.1}, z: {:.1} }}", self.v3.x, self.v3.y, self.v3.z)?;
        writeln!(f, "c: {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", self.c.r, self.c.g, self.c.b)?;
        writeln!(f, "sl:")?;
        for s in &self.sl {
            writeln!(f, "    {}", s)?;
        }
        writeln!(f, "v2l:")?;
        for v2 in &self.v2l {
            writeln!(f, "    {{ x: {:.1}, y: {:.1} }}", v2.x, v2.y)?;
        }
        writeln!(f, "v3l:")?;
        for v3 in &self.v3l {
            writeln!(f, "    {{ x: {:.1}, y: {:.1}, z: {:.1} }}", v3.x, v3.y, v3.z)?;
        }
        writeln!(f, "cl:")?;
        for c in &self.cl {
            writeln!(f, "    {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", c.r, c.g, c.b)?;
        }
        writeln!(f, "cx:")?;
        writeln!(f, "  identifier: {:#04X}", self.cx.identifier)?;
        writeln!(f, "  label: {}", self.cx.label)?;
        writeln!(f, "  text_color: {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", self.cx.text_color.r, self.cx.text_color.g, self.cx.text_color.b)?;
        writeln!(f, "  background_color: {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", self.cx.background_color.r, self.cx.background_color.g, self.cx.background_color.b)?;
        writeln!(f, "  spectrum:")?;
        for c in &self.cx.spectrum {
            writeln!(f, "    {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", c.r, c.g, c.b)?;
        }
        writeln!(f, "cxl:")?;
        for cx in &self.cxl {
            writeln!(f, "    identifier: {:#04X}", cx.identifier)?;
            writeln!(f, "    label: {}", cx.label)?;
            writeln!(f, "    text_color: {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", cx.text_color.r, cx.text_color.g, cx.text_color.b)?;
            writeln!(f, "    background_color: {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", cx.background_color.r, cx.background_color.g, cx.background_color.b)?;
            writeln!(f, "    spectrum:")?;
            for c in &cx.spectrum {
                writeln!(f, "      {{ r: {:#04x}, g: {:#04x}, b: {:#04x} }}", c.r, c.g, c.b)?;
            }
        }
        write!(f, "")
    }
}

fn main() {
    let filename = "../../../out/data/basic.c.msg";
    let buffer = fs::read(&filename).unwrap();

    let mut reader = BufferReader::new(buffer);
    let basic = TestingMessage::from_bytes(&mut reader).unwrap();
    println!("{}", basic);



    let mut out_data: Vec<u8> = Vec::new();
    let out = Vec2 { x: 1.0, y: 2.0 };
    out.write_bytes(&mut out_data);

    let filename = "../../../out/data/broken.rust.msg";
    fs::write(filename, out_data).unwrap();
}
