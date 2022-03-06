# handmade file to play around with some concepts for a Python
#   generator. right now just seeing how viable it would be to
#   use the built-in struct module as opposed to doing something
#   parallel to the other languages

from __future__ import annotations
import struct

msg_file = "../../../out/data/basic.c.msg"

class Color:
    def __init__(self):
        self.r: int = 0
        self.g: int = 0
        self.b: int = 0

    def __str__(self) -> str:
        return f"{{ r: {self.r}, g: {self.g}, b: {self.b} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(buffer: bytes) -> Color | None:
        ret = Color()
        try:
            ret.r, ret.g, ret.b = struct.unpack("BBB", buffer)
            return ret
        except struct.error:
            return None

class Vec2:
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0

    def __str__(self) -> str:
        return f"{{ x: {self.x}, y: {self.y} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(buffer: bytes) -> Vec2 | None:
        ret = Vec2()
        try:
            ret.x, ret.y = struct.unpack("<ff", buffer)
            return ret
        except struct.error:
            return None

class Vec3:
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        self.z: float = 0.0

    def __str__(self) -> str:
        return f"{{ x: {self.x}, y: {self.y}, z: {self.z} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def from_bytes(buffer: bytes) -> Vec3 | None:
        ret = Vec3()
        try:
            ret.x, ret.y, ret.z = struct.unpack("<fff", buffer)
            return ret
        except struct.error:
            return None


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

    # imagining the generator marching through the members
    #    building up a of things to unpack into, along with a format string
    #    once it hits a non-simple member, it calls an unpack
    # this is kinda cute, but is it worth having such a different
    #    approach from the other languages?
    # eh, what good is using a scripting language if you can't
    #    have a little fun with it?
    def from_bytes(buffer: bytes) -> TestingMessage | None:
        ret = TestingMessage()
        try:
            # using the memoryview keeps the buffer from copying
            #   every time we take a slice
            view = memoryview(buffer)
            pos = 0
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
            ) = struct.unpack("<B?hHiIqQfdI", view[:46])
            pos += 46
            (
                ret.s,
                ret.v2.x,
                ret.v2.y,
                ret.v3.x,
                ret.v3.y,
                ret.v3.z,
                ret.c.r,
                ret.c.g,
                ret.c.g,
                il_len,
            ) = struct.unpack(f"<{s_len}sfffffBBBI", view[pos : pos + s_len + 27])
            pos += s_len + 27
            ret.s = ret.s.decode('utf-8')
            ret.il = list(struct.unpack(f"<{il_len}h", view[pos : pos + (il_len * 2)]))
            pos += il_len * 2
            sl_len = struct.unpack(f"<I", view[pos:pos+4])[0]
            pos += 4
            for _ in range(sl_len):
                s_len = struct.unpack(f"<I", view[pos:pos+4])[0]
                pos += 4
                ret.sl.append(struct.unpack(f"<{s_len}s", view[pos:pos+s_len])[0].decode('utf-8'))
                pos += s_len
            v2l_len = struct.unpack(f"<I", view[pos:pos+4])[0]
            pos += 4
            for _ in range(v2l_len):
                v2 = Vec2()
                v2.x, v2.y = struct.unpack("<ff", view[pos:pos+8])
                ret.v2l.append(v2)
                pos += 8
            v3l_len = struct.unpack(f"<I", view[pos:pos+4])[0]
            pos += 4
            for _ in range(v3l_len):
                v3 = Vec3()
                v3.x, v3.y, v3.z = struct.unpack("<fff", view[pos:pos+12])
                ret.v3l.append(v3)
                pos += 12
            cl_len = struct.unpack(f"<I", view[pos:pos+4])[0]
            pos += 4
            for _ in range(cl_len):
                c = Color()
                c.r, c.g, c.b = struct.unpack("<BBB", view[pos:pos+3])
                ret.cl.append(c)
                pos += 3

            return ret
        except struct.error as e:
            print(e)
            return None


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

