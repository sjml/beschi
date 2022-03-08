# handmade file to play around with some concepts for a Python
#   generator. right now just seeing how viable it would be to
#   use the built-in struct module as opposed to doing something
#   parallel to the other languages

from __future__ import annotations
import struct

msg_file = "../../../out/data/basic.c.msg"

class _DataReader:
    def __init__(self, buffer: bytes|bytearray):
        # using a memoryview keeps the buffer from copying
        #   every time we take a slice
        self.mv = memoryview(buffer)
        self.current_position = 0

    def __del__(self):
        self.mv.release() # this is likely redundant?

    def is_finished(self) -> bool:
        return self.current_position >= len(self.mv)

    def has_remaining(self, size: int) -> bool:
        if self.current_position + size > len(self.mv):
            return False
        return True

    def take(self, amount: int):
        if not self.has_remaining(amount):
            raise IndexError("end of file reached prematurely")
        ret = self.mv[self.current_position:self.current_position+amount]
        self.current_position += amount
        return ret


class Color:
    def __init__(self):
        self.r: int = 0
        self.g: int = 0
        self.b: int = 0

    def __str__(self) -> str:
        return f"{{ r: {self.r}, g: {self.g}, b: {self.b} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(dr: _DataReader) -> Color:
        ret = Color()
        ret.r, ret.g, ret.b = struct.unpack("BBB", dr.take(3))
        return ret

class Vec2:
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0

    def __str__(self) -> str:
        return f"{{ x: {self.x}, y: {self.y} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(dr: _DataReader) -> Vec2:
        ret = Vec2()
        ret.x, ret.y = struct.unpack("<ff", dr.take(8))
        return ret

class Vec3:
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0

    def __str__(self) -> str:
        return f"{{ x: {self.x}, y: {self.y}, z: {self.z} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(dr: _DataReader) -> Vec3:
        ret = Vec3()
        ret.x, ret.y, ret.z = struct.unpack("<fff", dr.take(12))
        return ret

class ComplexData:
    def __init__(self):
        self.identifier: int = 0
        self.label: str = ""
        self.textColor: Color = Color()
        self.backgroundColor: Color = Color()
        self.spectrum: list[Color] = []

    def __str__(self) -> str:
        return f"{{ id: {self.identifier}, label: \"{self.label}\", textColor: {self.textColor}, backgroundColor: {self.backgroundColor}, spectrum: {self.spectrum} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(dr: _DataReader) -> ComplexData:
        ret = ComplexData()
        (ret.identifier, label_len) = struct.unpack("<BI", dr.take(5))
        (
            ret.label,
            ret.textColor.r,
            ret.textColor.g,
            ret.textColor.b,
            ret.backgroundColor.r,
            ret.backgroundColor.g,
            ret.backgroundColor.b,
            spectrum_len
        ) = struct.unpack(f"<{label_len}sBBBBBBI", dr.take(label_len + 10))
        ret.label = ret.label.decode('utf-8')
        for _ in range(spectrum_len):
            el = Color()
            el.r, el.g, el.b = struct.unpack("<BBB", dr.take(3))
            ret.spectrum.append(el)
        return ret


class TestingMessage:
    def __init__(self):
        self.b: int = 0
        self.tf: bool = 0
        self.i16: int = 0
        self.ui16: int = 0
        self.i32: int = 0
        self.ui32: int = 0
        self.i64: int = 0
        self.ui64: int = 0
        self.f: float = 0.0
        self.d: float = 0.0
        self.s: str = ""
        self.v2: Vec2 = Vec2()
        self.v3: Vec3 = Vec3()
        self.c: Color = Color()
        self.il: list[int] = []
        self.sl: list[str] = []
        self.v2l: list[Vec2] = []
        self.v3l: list[Vec3] = []
        self.cl: list[Color] = []
        self.cx: ComplexData = ComplexData()
        self.cxl: list[ComplexData] = []

    # imagining the generator marching through the members
    #    building up a list of things to unpack into, along with a format string
    #    once it hits a non-simple member, it calls an unpack
    # this is kinda cute, but is it worth having such a different
    #    approach from the other languages?
    # eh, what good is using a scripting language if you can't
    #    have a little fun with it?
    def from_bytes(buffer: bytes) -> TestingMessage | None:
        dr = _DataReader(buffer)
        try:
            ret = TestingMessage()
            (
                ret.b,
                ret.tf,
                ret.i16,
                ret.ui16,
                ret.i32,
                ret.ui32,
                ret.i64,
                ret.ui64,
                ret.f,
                ret.d,
                s_len,
            ) = struct.unpack("<B?hHiIqQfdI", dr.take(46))
            (
                ret.s,

                # note that simple structs like Vec2/Vec3/Color can just be
                #   inlined here instead of calling out to their from_bytes methods
                # do those methods need to be generated at all?
                #   (same question for other languages -- dead code usually
                #    isn't a problem since compilers just remove it, but
                #    worth thinking about. [rust warns, for example])
                ret.v2.x,
                ret.v2.y,
                ret.v3.x,
                ret.v3.y,
                ret.v3.z,
                ret.c.r,
                ret.c.g,
                ret.c.g,
                il_len,
            ) = struct.unpack(f"<{s_len}sfffffBBBI", dr.take(s_len + 27))
            ret.s = ret.s.decode('utf-8')
            ret.il = list(struct.unpack(f"<{il_len}h", dr.take(il_len * 2)))

            # question: is unpack efficient when taking just a single value?
            #   memoryview also has a "cast" function
            #   https://docs.python.org/3/library/stdtypes.html#memoryview.cast
            # probably not worth introducing another generator path; as written
            #   here it is consistent with the other methods
            sl_len, = struct.unpack(f"<I", dr.take(4))
            for _ in range(sl_len):
                (el_len, ) = struct.unpack(f"<I", dr.take(4))
                (el, ) = struct.unpack(f"<{el_len}s", dr.take(el_len))
                el = el.decode('utf-8')
                ret.sl.append(el)
            v2l_len, = struct.unpack(f"<I", dr.take(4))
            for _ in range(v2l_len):
                el = Vec2()
                (el.x, el.y) = struct.unpack("<ff", dr.take(8))
                ret.v2l.append(el)
            v3l_len, = struct.unpack(f"<I", dr.take(4))
            for _ in range(v3l_len):
                el = Vec3()
                el.x, el.y, el.z = struct.unpack("<fff", dr.take(12))
                ret.v3l.append(el)
            cl_len, = struct.unpack(f"<I", dr.take(4))
            for _ in range(cl_len):
                el = Color()
                el.r, el.g, el.b = struct.unpack("<BBB", dr.take(3))
                ret.cl.append(el)
            ret.cx = ComplexData.from_bytes(dr)
            cxl_len, = struct.unpack(f"<I", dr.take(4))
            for _ in range(cxl_len):
                el = ComplexData.from_bytes(dr)
                ret.cxl.append(el)

            return ret
        except Exception as e:
            # raise e
            return None
        finally:
            del dr


buffer = open(msg_file, "rb").read()
tm = TestingMessage.from_bytes(buffer)

if tm:
    print(tm.b)
    print(tm.tf)
    print(tm.i16)
    print(tm.ui16)
    print(tm.i32)
    print(tm.ui32)
    print(tm.i64)
    print(tm.ui64)
    print(tm.f)
    print(tm.d)
    print(tm.s)
    print(tm.v2)
    print(tm.v3)
    print(tm.c)
    print(tm.il)
    print(tm.sl)
    print(tm.v2l)
    print(tm.v3l)
    print(tm.cl)
    print(tm.cx)
    print(tm.cxl)
