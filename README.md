# Beschi

[![PyPI](https://img.shields.io/pypi/v/beschi)](https://pypi.org/project/beschi/) [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/sjml/beschi/ci.yml)](https://github.com/sjml/beschi/actions/workflows/ci.yml)

This is a custom bit-packing and unpacking code generator for C, C#, Go, Rust, Swift, and TypeScript. You feed it a data description and it generates source files for writing/reading buffers of that data, along the lines of [FlatBuffers](https://google.github.io/flatbuffers/) or [Cap'n Proto](https://capnproto.org), but with much less functionality for much simpler use cases. It was initially written for a larger project that was passing data back and forth between a Unity game, a Go server, and a web client, but I extracted it into its own thing. If all you need is a simple way to pack a data structure into a compact, portable binary form, this might be useful for you.

I go into more explanation for why this exists [in the documentation](https://github.com/sjml/beschi/blob/main/docs/), but I'll be honest, too: it **was** kind of fun to write a code generator. 😝 


## Documentation

* [Introduction](https://github.com/sjml/beschi/blob/main/docs/introduction.md)
* [Protocols](https://github.com/sjml/beschi/blob/main/docs/protocols.md)

Language-Specific Documentation: 

| [C](https://github.com/sjml/beschi/blob/main/docs/languages/c.md) | [C#](https://github.com/sjml/beschi/blob/main/docs/languages/csharp.md) | [Go](https://github.com/sjml/beschi/blob/main/docs/languages/go.md) | [Rust](https://github.com/sjml/beschi/blob/main/docs/languages/rust.md) | [Swift](https://github.com/sjml/beschi/blob/main/docs/languages/swift.md) | [TypeScript](https://github.com/sjml/beschi/blob/main/docs/languages/typescript.md) |
|-|-|-|-|-|-|

* [Dev Notes](https://github.com/sjml/beschi/blob/main/docs/dev)


## Installation

If you use [Homebrew](https://brew.sh), you can install it directly and simply: 

```
brew install sjml/sjml/beschi
```

Otherwise, you need a Python setup and can then install from [PyPI](https://pypi.org/project/beschi/): 

```
pip install beschi
```

It installs an executable that you can run directly, so long as however you invoked `pip` put it on your path. (This will work in an activated virtual environment, for instance.)

Example:
```
beschi --lang csharp --protocol ./messages.toml
```

## Basic Usage

By default, it prints to standard output, but you can also write to a file with an output flag like `--output ./Messages.cs`.

From the input protocol file (detailed below), you get a code file that you can integrate to a project allowing you encode messages as compact and portable binary buffers. 


## Protocols

The protocol files are written in [TOML](https://toml.io). There's [a fuller example in the test suite](https://github.com/sjml/beschi/tree/main/test/_protocols/example.toml) and a [more through explanation in the documentation](https://github.com/sjml/beschi/blob/main/docs/protocols.md), but here's an annotated sample.

```toml
[meta]
# The namespace is optional; not all languages
#  do something useful with it, but it's handy
#  to have to help avoid clashes
namespace = "AppMessages"

# Messages are defined by a name and their data
#  members. This will become a class or struct in
#  the target languages with these pieces of data
#  as accessible members.
[[messages]]
_name = "Vector3Message"
x = "float"
y = "float"
z = "float"

# There are a variety of different data member
#  types that can be defined.
[[messages]]
_name = "NewCharacterMessage"
id = "uint64"
characterName = "string"
strength = "uint16"
intelligence = "uint16"
dexterity = "uint16"
goldInWallet = "uint32"
nicknames = "[string]" # brackets indicate a list/array

# You can also define structs, collections of data
#  that go together, but are not themselves a message.
[[structs]]
_name = "Color"
red = "float"
green = "float"
blue = "float"
alpha = "float"

# Structs can contain other structs, and even lists of them.
[[structs]]
_name = "Spectrum"
defaultColor = "Color"
colors = "[Color]"

# Structs can then be used in messages.
[[messages]]
_name = "CharacterJoinedTeam"
characterID = "uint64"
teamName = "string"
teamColors = "[Color]"
```

## Data Members

These are the base types from which you can build up whatever structures and messages you need to, along with what they correspond to in the various languages. 

| Protocol Type | C          | C#       | Go        | Rust     | Swift     | TypeScript |
|---------------|------------|----------|-----------|----------|-----------|------------|
| `byte`        | `uint8_t`  | `byte`   | `byte`    | `u8`     | `UInt8`   | `number`   |
| `bool`        | `bool`     | `bool`   | `bool`    | `bool`   | `Bool`    | `boolean`  |
| `int16`       | `uint16_t` | `short`  | `int16`   | `i16`    | `Int16`   | `number`   |
| `uint16`      | `int16_t`  | `ushort` | `uint16`  | `u16`    | `UInt16`  | `number`   |
| `int32`       | `uint32_t` | `int`    | `int32`   | `i32`    | `Int32`   | `number`   |
| `uint32`      | `int32_t`  | `uint`   | `uint32`  | `u32`    | `UInt32`  | `number`   |
| `int64`       | `uint64_t` | `long`   | `int64`   | `i64`    | `Int64`   | `bigint`   |
| `uint64`      | `int64_t`  | `ulong`  | `uint64`  | `u64`    | `UInt64`  | `bigint`   |
| `float`       | `float`    | `float`  | `float32` | `f32`    | `Float32` | `number`   |
| `double`      | `double`   | `double` | `float64` | `f64`    | `Float64` | `number`   |
| `string`      | `char*`    | `string` | `string`  | `String` | `String`  | `string`   |

All the numbers are stored as little-endian in the buffer, if that matters for you. 


## Usage in code

Beschi does not generate any code to handle writing or reading from disk, pushing data across a network, or anything like that — it will turn a message into bytes and read that same message back from the bytes, but you are responsible for what you do with them otherwise. 

With the given protocol, though, you could create a message in C# and write it to a file:
```csharp
var msg = new AppMessages.Vector3Message();
msg.x = 1.0f;
msg.y = 4096.1234f;
msg.z = -42.56f;
var fs = new FileStream("./vec3.msg", FileMode.Create);
var bw = new BinaryWriter(fs);
msg.WriteBytes(bw, false);
```

And then read it back in TypeScript:
```typescript
const data = fs.readFileSync("./vec3.msg");
const dv = new DataView(new Uint8Array(data).buffer);
const msg = AppMessages.Vector3Message.FromBytes(dv, 0).val;
if (msg.y == Math.fround(4096.1234)) {
    console.log("Ready to go!");
}
```

Or Go:
```golang
dat, _ := os.Open("./vec3.msg")
defer dat.Close()
msg := AppMessages.Vector3MessageFromBytes(dat)
if msg.X == 1.0 && msg.Y == 4096.1234 && msg.Z < 0.0 {
	print("Ready to go!\n")
}
```

For the most part, Beschi tries to keep behavior and structures consistent across the languages, but there are a few points of difference [outlined on the various language pages](https://github.com/sjml/beschi/blob/main/docs/languages). Notice in the example above, for instance, that in TypeScript you have to make a call to `Math.fround` if you want to do a straight comparison of float values because of how the underlying JavaScript engine treats all numbers as double-width floats. (Doing equality comparisons on floats is usually a bad idea, but in this instance we *want* to check that they are actually bitwise identical.) Similarly, see how the data members are upper-cased in Go to match that language's export conventions, and the byte reading function is part of the namespace because Go doesn't have static functions for data types. The goal is to make working across languages feel as seamless as possible, but there are some differences that we adapt to as much as possible. 

There are more extensive examples in [the test harnesses](https://github.com/sjml/beschi/tree/main/test/_harnesses).


## Future

Beschi makes code that I use "in production" on personal projects. It could probably stand to be better optimized, there are probably edge cases and bugs, etc. But for the most part, this is mature enough that I stopped thinking of it as a project in itself and now it's just a tool that I use. 

I will admit that part of me wants to make new writers, but that's not likely to get done until I have a specific project motivating it. If someone loves this system, though, and really wants to see a generator for Haskell or Lua or whatever, go for it. The existing writers should be decent starting points — they aren't terribly clever (no AST or interesting data structures), just iterating over the protocol and writing out serialization/deserialization code. 


## Beschi?

[Constanzo Giuseppe Beschi](https://en.wikipedia.org/wiki/Constanzo_Beschi) was an Italian Jesuit who worked in southern India during the early 18th century. He was noted as a talented linguist, able to tie concepts from multiple languages into a single form. At the same time, he was adept at the Jesuit principle of "inculturation," where foreign concepts are adapted for a new culture and the foreigner attempting the adaptation also respectfully adopts habits and ways of proceeding from the host culture.

