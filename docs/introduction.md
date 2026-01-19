# How to Use Beschi

This is a general introduction to Beschi as a whole. Once you're done reading this, you'll probably want to check out the [more specific documentation](./languages/) for your desired language(s). 

| [C](./languages/c.md) | [C#](./languages/csharp.md) | [Go](./languages/go.md) | [Rust](./languages/rust.md) | [Swift](./languages/swift.md) | [TypeScript](./languages/typescript.md) | [AssemblyScript](./languages/assemblyscript.md) | [Zig](./languages/zig.md)
|-|-|-|-|-|-|-|-|


## Do you even want to?

If you're working on a program that has to share data, especially with other programs written in different languages, you have a few options for how to format that data. [JSON](https://en.wikipedia.org/wiki/JSON) is a very popular option, since it's simple, human-readable, well-supported, and in a convenient text format. It can be a little bulky, though, depending on your use case, and performance becomes a problem if the data gets very large. 

Other solutions are things like [FlatBuffers](https://google.github.io/flatbuffers/) or [Cap'n Proto](https://capnproto.org), which produce efficient binary representations of data which can be directly mapped into memory. They also allow for things like partial deserialization (taking a subset of the data without having to read the whole file), versioning data (so you can modify your formats and have old messages still be readable). However, using the data within your code requires some awkward serialization and deserialization code before you have the information in usable form. 

If you're willing to give up some of the benefits of those more advanced binary formats in exchange for **much** simpler code in your client programs, then you might like Beschi. 

> For the record, my own motivating project that started this (when it was only generating code for C#, TypeScript, and Go), was ephemeral messages being passed between a mobile browser, a server which filtered/processed, and a Unity game which ran a small simulation. All were bundled together into a single app package, so I knew they were always updating in lockstep (no need to deal with different message versions); the messages were not retained beyond their transmission (no need to keep reading older messages); all three languages basically needed access to all of the message (no point in partial deserialization); I had ample memory and CPU budget (no need to be super efficient); I wanted to minimize the size of transmitted data (something like JSON was too big); I wanted strong typing (JSON is too ad-hoc). With that particular set of needs, Beschi is a reasonable choice over more feature-ful systems. 


## How does it work?

Beschi is a tool that generates source code. You describe the kind of message you want to send and receive, and Beschi generates source code to read and write that message to a compact memory buffer. 

For example, we could specify the following message: 
```toml
[[messages]]
_name = "Position"
x = "float"
y = "float"
z = "float"
```

Beschi will read this file and generate code that lets you use that data like so in C#: 
```csharp
var pos = new Position();
pos.x = 1.0f;
pos.y = -2.0f;
pos.z = 3.0f;

byte[] buffer = new byte[pos.GetSizeInBytes()];
MemoryStream m = new MemoryStream(buffer);
BinaryWriter bw = new BinaryWriter(m);
pos.WriteBytes(bw, true);
```

The code that handles creating the buffer and making a writable stream from it is particular to the .NET system libraries that C# uses, but every language that Beschi targets has some similar kind of functionality. The important thing is that final call, where the data is written into the buffer. Once you have that buffer, you can do whatever you want with it -- send it across a network, write it to disk, etc. 

You can create more complicated data types and messages, too; this was a very simplified example. For more information, look at the [protocol documentation](./protocols.md).


## Generated Code

You can see [examples of the generated code in each target language](./generated_examples/), made from [this data protocol](../test/_protocols/annotated.toml). 

For the most part, Beschi does its best to keep behavior and data structures consistent across the languages That desire for consistency, though, is balanced with wanting the code to feel at home in each language, so it adapts to specific language conventions and best practices as best it can. You can read about the particular exceptions made for each language in the caveats sections of its documentation page.

You should think of the generated code files as effectively "compiled;" that is, you shouldn't edit them directly, but rather make changes to your protocol file and re-generate them. While the generated code is not intentionally obfuscated, it's also not meant to be read by humans _per se_, so take that into account. That said, the generated code **should** be a good citizen in each host language, making best use of available idioms, etc. If you think Beschi is generating sub-optimal code for a given language, please file an issue. 


### Structures and Methods

Each language works a little bit differently, but in general you should expect to find these functions or something very similar to them in every generated code file. Differences from this are noted in [each language's specific documentation](./languages/).

* `Message` class: a base class that each message inherits from. It provides the following methods:
    * `GetMessageType()`: returns an enum value that identifies what specific type of message the object represents
    * `GetSizeInBytes()`: returns the size of memory buffer required to write out the message in its current form. If the message and its data members don't contain strings or lists, this is pre-calculated and constant. Otherwise, though, it has to run some calculations to measure out string length, number of items in a list, etc. (This function returns whatever kind of numeric type the target language expects for allocating buffers, so `size_t` in C, `int` in C#, etc.)
    * `WriteBytes(buffer, tag)`: takes the language's equivalent of a data buffer and a boolean value to indicate whether to tag the written data by writing the identifier (from `GetMessageType()`) in front of it. 
    * `FromBytes(buffer)`: a static function that returns a message of the class's type, or a null value if it could not be parsed. This is useful if you already know what kind of message you're expecting from a certain buffer and don't need to identify it beforehand. 

Each namespace (or generated file) contains a function for handling a buffer containing multiple messages:
* `ProcessRawBytes(buffer)`: takes a buffer and returns a list/array of Message objects. The messages in the buffer need to be tagged with their identifiers. Note that if it encounters a stretch of memory that it cannot parse, it will throw an exception or return an error value. 


## Caveats and Limitations

Beschi is a little fast and loose with how it does does code generation. This allows for simpler generator code (each language writer is around just 200-500 lines of fairly readable [if somewhat belabored] imperative code without layers of templates) without dependencies, but it does mean that there are some situations it can't handle. 

* I make no claims that the generated code is optimal or necessarily even good. It passes [a test suite](./../test/), and I've used it "in production" for personal projects; it seems to work pretty well, but I'm not an expert programmer in all the target languages, so am very open to feedback if there's something that could be improved. 
* The test suite is not completely exhaustive. It tests some pathological inputs like infinite inclusion loops and deeply nested structures (for some definition of "deep") but you could probably devise a protocol that would make it fall over. Let me know if you do! 
* It makes efforts to generate code that follows the best practices of each language as much as possible, but that code probably won't win any awards from the linters. The test suite runs with warnings as high as recommended by compilers (clang used to run with `-Weverything` but [even they don't recommend that](https://clang.llvm.org/docs/UsersManual.html#diagnostics-enable-everything)), and there are a few very specific warnings in each language that it suppresses.
* It always produces *valid* code (if it does not, that is a bug), but it may not be formatted to your (or `gofmt`'s) liking. If you have strong opinions on that sort of thing, consider running it through a code formatter after generation.
* Beschi makes no attempt to limit variable names other than disallowing whitespace and making sure the protocol itself is valid. That means you could name a data member something that is a reserved word in a target language and it would cause compilation problems. Or you could use emoji for all your structure names because you're only working in Swift and find that nothing works in C. If you call something "return" or "💩" you probably won't be happy, so don't do that; stay happy.
* You cannot at present define more than 255 message types in a single namespace. This is because the identifier tag is a single byte. It hasn't proven to be a limitation for me so far, and it could obviously be expanded if needed. 
* Strings and lists default to using an unsigned 32-bit integer to record their lengths in the buffers. That's enough for more than 4 GB of ASCII text in a string; if you need more, you probably outgrew this system long ago. If it's too much and you want to save every byte, or if you want even more space, you can [specify a different type](./protocols.md#meta-section).
    * **IMPORTANT NOTE**: The size limits are *not* enforced in the generated code. They are a promise you make to the system, not a law you are laying down. If you say that list sizes can be stored in a byte, but then try to store a list with 300 values, behavior is undefined; each generated language fails in different ways, perhaps mysteriously. 
