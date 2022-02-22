# Beschi

![continuous integration](https://github.com/sjml/beschi/actions/workflows/ci.yml/badge.svg)

This is a custom bit-packing and unpacking code generator for C#, Go, and TypeScript. It was written for a larger project but I extracted it into its own thing.

The original project started off using [FlatBuffers](https://google.github.io/flatbuffers/), which are actually pretty great for a lot of use cases and I definitely recommend you look at them if you want something with more functionality and polish. However, for the original project I needed the actual produced buffers to be as tiny as possible — with FlatBuffers, the resulting data is a little bulky because of the vtables and support for changing schema while still being able to use old data. Since messages only exist in flight and are never persisted, client and server can stay in lockstep, so the bytestreams can be more compact. The code for creating and reading messages with Beschi is also a bit smoother... at least, it's a bit more to my personal tastes in code.

Beschi messages also lose the FlatBuffer benefit of being able to snag data out without fully deserializing, but in my use case (a) most messages are very small and (b) I basically *always* want *all* the data. So for this particular use case, I can lose the overhead and have some more ergonomic client code. 

I'll be honest, too: it **was** kind of fun to write a code generator. 😝 


## How to use

Eventually I'll put this in [PyPI](https://pypi.org/), but for now, install with pip or your favorite Python packaging system. 

```
pip install git+https://github.com/sjml/beschi.git
```

It creates a binary file that you can run directly, so long as however you invoked `pip` put it on your path. (This will work in an activated virtual environment, for example.)

Example:
```
beschi --lang csharp --protocol ./messages.toml
```

By default, it prints to stdout, but you can also go direct to a file with and output flag like `--output ./Messages.cs`.

From the protocol file (detailed below), you get a code file that you can integrate to a project allowing you encode messages as compact and portable binary streams. For example, I used it in a project where Unity, a Go server, and a web client were all passing data back and forth to each other. When the message format had to change, it was just a matter of changing the protocol file and regenerating the language files, instead of the painstaking and error-prone manual bit-packing and unpacking. 


## Protocols

The protocol files are built in [TOML](https://toml.io). There's [a fuller example in the test suite](test/_protocols/example.toml), but here's an annotated sample.

```toml
# the "meta" section only has the namespace
#  for now, but may have more later if needed
#
# the namespace is optional; not all languages
#  do something useful with it, but it's handy
#  to have to help avoid clashes
[meta]
namespace = "AppMessages"

# messages are defined by a name and their data
#  members. this will become a class or struct in
#  the target languages with these pieces of data
#  as accessible members.
[[messages]]
_name = "Vector3Message"
x = "float"
y = "float"
z = "float"

# there are a variety of different data member
#  types that can be defined
[[messages]]
_name = "NewCharacterMessage"
id = "uint64"
characterName = "string"
strength = "uint16"
intelligence = "uint16"
dexterity = "uint16"
goldInWallet = "uint32"
nicknames = "[string]" # the brackets indicate a list/array

# you can also define structs, collections of data
#  that go together, but are not themselves a message
[[structs]]
_name = "Color"
red = "float"
green = "float"
blue = "float"
alpha = "float"

# structs can contain other structs, and even lists of them
[[structs]]
_name = "Spectrum"
defaultColor = "Color"
colors = "[Color]"

# structs can then be used in messages
[[messages]]
_name = "CharacterJoinedTeam"
characterID = "uint64"
teamName = "string"
teamColors = "[Color]"
```

## Data Members

These are the base types from which you can build up whatever structures and messages you need to, along with what they correspond to in the various languages. 

| Protocol Data Type | C#      | TypeScript | Go      |
|--------------------|---------|-----------|-----------|
| `byte`             | `byte`  | `number`  | `byte`    |
| `bool`             | `bool`  | `boolean` | `bool`    |
| `int16`            | `short` | `number`  | `int16`   |
| `uint16`           | `ushort`| `number`  | `uint16`  |
| `int32`            | `int`   | `number`  | `int32`   |
| `uint32`           | `uint`  | `number`  | `uint32`  |
| `int64`            | `long`  | `bigint`  | `int64`   |
| `uint64`           | `ulong` | `bigint`  | `uint64`  |
| `float`            | `float` | `number`  | `float32` |
| `double`           | `double`| `number`  | `float64` |


All the numbers are stored little-endian in the bytestream, if that matters for you. 


## Usage in code

Beschi does not generate any code to handle writing or reading from disk, pushing data across a network, or anything like that — it will turn a message into bytes and read that same message back from the bytes, but you are responsible for what you do with the bytes between those points. 

With the given protocol, though, you could write a message in C#:

```csharp
var msg = new AppMessages.Vector3Message();
msg.x = 1.0f;
msg.y = 4096.1234f;
msg.z = -42.56f;
var fs = new FileStream("./vec3.msg", FileMode.Create);
var bw = new BinaryWriter(fs);
msg.WriteBytes(bw, false);
```

And read it back in TypeScript:

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

For the most part Beschi tries to keep behavior and structures consistent across the languages, but there are a few points of difference outlined in detail below. Notice that in TypeScript you have to make a call to `Math.fround` if you want to do a straight comparison of float values because of how the underlying JavaScript engine treats all numbers as double-width floats. Or how the data members are upper-cased in Go to match that language's export conventions, and the byte reading function is part of the namespace because Go doesn't have static functions for data types. The goal is to have working across languages feel as seamless as possible, but differences are outlined in the specific language sections below. 

There are more extensive examples in [the test harnesses](test/_harnesses).

## Message objects

(In the function signature pseudocode below, [...] indicates that specific languages may need additional parameters; these are the bases that indicate broad functionality.)

Messages are instantiated with each language's standard construction style. 

Go:
```golang
var vec3 AppMessages.Vector3Message
vec3.x = 1.0
vec3.y = 2.0
vec3.z = 3.0
```

C#: 
```csharp
var vec3 = new AppMessages.Vector3Message();
vec3.x = 1.0f;
vec3.y = 2.0f;
vec3.z = 3.0f;
```

TypeScript:
```typescript
const vec3 = new AppMessages.Vector3Message();
vec3.x = 1.0;
vec3.y = 2.0;
vec3.z = 3.0;
```

Note that all data members are initialized to zero values (or empty strings/lists). There's no way, at present, to specify other defaults in a protocol, so that needs to be handled in client code. 

Instances of the Message base class (interface in Go) defines three methods: 
* `GetMessageType()`: returns an enum value that identifies what specific type of message the object represents
* `GetSizeInBytes()`: returns the size of memory buffer required to write out the message in its current form. If the message and its data members don't contain strings or lists, this is pre-calculated. Otherwise, though, it has to run some calculations to measure out string length, number of items in a list, etc. 
* `WriteBytes(buffer, tag, [...])`: takes the language's equivalent of a data buffer and a boolean value to indicate whether to tag the written data by writing the identifier (from `GetMessageType()`) in front of it. 

Each namespace (or generated file) contains a function for handling a buffer containing multiple messages:
* `ProcessRawBytes(buffer, [...])`: takes a buffer and returns a list/array of Message objects. The messages in the buffer need to be tagged with their identifiers. Note that if it encounters a stretch of memory that it cannot parse, it will append a nil value and stop processing, returning the set of messages parsed so far. 

Each Message class also has a static function in languages that allow it:
* `FromBytes(buffer, [...])`: returns a message of the class's type, or a null value if it could not be parsed. This is useful if you already know what kind of message you're expecting from a certain buffer and don't need to identify it beforehand. 

Note that generated struct objects also have `WriteBytes` and `FromBytes` equivalents, but they need to be used with a little more caution since they throw exceptions (or panic) on errors where Messages will return a null value.

## Caveats

Beschi is a little bit fast and loose with how it does generation. This allows for simpler generator code (each language writer is just around 400 lines of fairly readable declarative code without layers of templates) and necessitates fewer dependencies (only TOML so far!), but it does mean that there are some situations it can't handle. 

### General
* It makes efforts to follow the best practices of each language as much as possible, but the generated code probably won't win any awards from linters. 
* It always produces *valid* code (if it does not, that is a bug), but it may not be formatted to your (or gofmt's) liking. If you have strong opinions on that sort of thing, consider running it through a code formatter program after generation.
* Makes no attempt to limit variable names other than disallowed whitespace. That means you could name a data member something that is a reserved word in a target language and it would cause compilation problems. If you call a message member "int" you probably won't be happy, so don't do that; stay happy.
* There are probably some protocols you can define that produce invalid code in the target languages. I'm thinking specifically of some pathological cases of a bunch of nested structs where all data members are called the same thing. So don't do that either. 
* You cannot at present define more than 255 message types in a single namespace. This is because the identifier tag is a single byte at the moment. This hasn't proven to be a limitation for me so far, and it could obviously be expanded if needed. 
* Strings and lists use an unsigned 32-bit integer to record their lengths in the buffers. That's enough for more than 4 GB of ASCII text in a string; if that's more than you need, you probably outgrew this system long ago.
* There is no effort made at checking data integrity or the like. It would not be too hard to add a checksum message or data member and perform that verification in client code, though. 
* There is no partial deserialization, like with FlatBuffers, where you can just snag a specific piece of data out of the stream. I mostly work with small messages that I always want to fully decode, so this was just added overhead; if that's something you need, consider other options. 
* There is no functionality for versioning messages, so if you update your data format, the old messages will not be able to be read by new code. These messages are not meant to persist beyond the time it takes to shuttle them across a network or memory pipe. Versioning can be accomplished on the client side, but will require manual decoding steps and probably retaining the old generated reading code.


### Go
* Usually the identifying enum is accessed by `{namespace}.MessageType.{specific_message_name}Type`, but Go doesn't do enums the way the other languages do, so it's missing the `.MessageType.` in the middle. 
* The generated Go code uses the standard binary readers and writers, which allow for dealing with whole structures in one go. They seem to pack and unpack identically to the more detailed systems that the other languages need, but there might be some edge cases where packing becomes an issue. 
* Go doesn't have static functions, so instead of `AppMessages.Vector3Message.FromBytes()`, you call `AppMessages.Vector3MessageFromBytes()`.
* The various `*FromBytes` functions *on structs* also take a pointer to a variable of the appropriate Message type, which will get filled in as it reads. (For messages, you just pass a buffer and it either returns a poitner to the correct type or `nil`.)
* As mentioned above, generated Go code will have all the data members changed to start with an uppercase letter to match the language's export needs. 

### TypeScript
* Following [current recommendations from the TypeScript team](https://www.typescriptlang.org/docs/handbook/namespaces-and-modules.html), it ignores the defined namespace in favor of treating the whole exported code as a module. You can still get the same syntax by importing like: `import * as AppMessages from './AppMessages';`. 
* The generated TypeScript code uses decorators to provide something similar to static functions. There might be a better way of handling this, and I'm open to suggestion, but for now you have to have `experimentalDecorators` enabled in your TypeScript configuration. 
* 64-bit integers (both signed and unsigned) are implemented with BigInt, which has [pretty broad support at this point](https://caniuse.com/?search=bigint). Your client code may need to handle them differently though -- you can't easily do math with a regular `number` and a `bigint`. Users of other languages are used to these kinds of folds, but JavaScript/TypeScript users may find them new and annoying. :) 
* The generated `WriteBytes()` function for TypeScript takes an additional `offset: number` parameter. Since JavaScript doesn't keep track of a position when writing into a buffer, we have to manually tell it where to start writing. The function also returns a new offset letting you know where it finished writing. 
* Similarly, the TypeScript implementation of `ProcessRawBytes` also takes an offset parameter, and instead of just returning a list of Messages, returns an object: `{ vals: Message[], offset: number }`.
* `FromBytes` also takes an offset and returns a structure similar to the one from `ProcessRawBytes`: `{ val: SpecificMessageType, offset: number }`

### C#
* No particular caveats, actually! Perhaps a side effect of C# being the first generator that was made for this system is that its semantics match up pretty well. 


## Future
I will admit that part of me wants to make new writers, but since I don't have a project motivating that at the moment, it's not likely to get done. If someone loves this sytem, though, and really wants to see a generator for C or Swift or Rust or whatever, let me know. The existing writers should be decent starting points — they aren't terribly clever (no AST or interesting data structures), just iterating over the protocol and writing out serialization/deserialization code. 


## Beschi?
[Constanzo Giuseppe Beschi](https://en.wikipedia.org/wiki/Constanzo_Beschi) was an Italian Jesuit who worked in southern India during the early 18th century. He was noted as a talented linguist, able to tie concepts from multiple languages into a single form. At the same time, he was adept at the Jesuit principle of "inculturation," where foreign concepts are adapted for a new culture and the foreigner attempting the adaptation also respectfully adopts habits and ways of proceeding from the host culture.

