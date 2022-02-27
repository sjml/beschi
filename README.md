# Beschi

[![Verification Tests](https://github.com/sjml/beschi/actions/workflows/ci.yml/badge.svg)](https://github.com/sjml/beschi/actions/workflows/ci.yml)

This is a custom bit-packing and unpacking code generator for C#, Go, C, Swift, and TypeScript. You feed it a data description and it generates source files for writing/reading buffers of that data, along the lines of [FlatBuffers](https://google.github.io/flatbuffers/) or [Cap'n Proto](https://capnproto.org), but with much less functionality for much simpler use cases. It was initially written for a larger project but I extracted it into its own thing. If all you need is a simple way to pack a data structure into a compact, portable binary form, this might be useful for you.

The original project started off using FlatBuffers, which are pretty great for a lot of use cases and I definitely recommend you look at them if you need the features they offer. I faced two issues, though: 
1. The code for getting data in and out of FlatBuffers is super awkward.
2. The actual binary data created by flatbuffers is relatively bulky. 

Both of these problems stem from the fact that FlatBuffers provide a lot of interesting functionality like being able to update the data schema, partially deserialize data to pluck out a single element, etc. But I wasn't using any of that functionality -- since my messages only exist in flight and are never persisted, client and server can stay in lockstep, and the buffers can be more compact. Partial deserialization was not a benefit for me, since most of my messages were very small and I basically *always* need *all* the data. I didn't want an opaque buffer that I could munge data in and out of; I just wanted native language structures that I could package for transmission. So for this particular use case, I can lose the overhead, get smaller buffers, and have some easier-to-write client code.

I'll be honest, too: it **was** kind of fun to write a code generator. 😝 


## How to use

You can install from [PyPI](https://pypi.org/project/beschi/): 

```
pip install beschi
```

It installs an executable that you can run directly, so long as however you invoked `pip` put it on your path. (This will work in an activated virtual environment, for instance.)

Example:
```
beschi --lang csharp --protocol ./messages.toml
```

By default, it prints to standard output, but you can also write to a file with an output flag like `--output ./Messages.cs`.

From the input protocol file (detailed below), you get a code file that you can integrate to a project allowing you encode messages as compact and portable binary buffers. For example, I used it in a project where a Unity game, a Go server, and a web client were all passing data back and forth to each other. When the message format needed to change, it was just a matter of tweaking the protocol and regenerating the language files, instead of having to do the painstaking and error-prone manual bit-packing and unpacking across multiple languages. 


## Protocols

The protocol files are written in [TOML](https://toml.io). There's [a fuller example in the test suite](https://github.com/sjml/beschi/tree/main/test/_protocols/example.toml), but here's an annotated sample.

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

| Protocol Type | C#       | Go        | C          | Swift     | TypeScript |
|---------------|----------|-----------|------------|-----------|------------|
| `byte`        | `byte`   | `byte`    | `uint8_t`  | `UInt8`   | `number`   |
| `bool`        | `bool`   | `bool`    | `bool`     | `Bool`    | `boolean`  |
| `int16`       | `short`  | `int16`   | `uint16_t` | `Int16`   | `number`   |
| `uint16`      | `ushort` | `uint16`  | `int16_t`  | `UInt16`  | `number`   |
| `int32`       | `int`    | `int32`   | `uint32_t` | `Int32`   | `number`   |
| `uint32`      | `uint`   | `uint32`  | `int32_t`  | `UInt32`  | `number`   |
| `int64`       | `long`   | `int64`   | `uint64_t` | `Int64`   | `bigint`   |
| `uint64`      | `ulong`  | `uint64`  | `int64_t`  | `UInt64`  | `bigint`   |
| `float`       | `float`  | `float32` | `float`    | `Float32` | `number`   |
| `double`      | `double` | `float64` | `double`   | `Float64` | `number`   |
| `string`      | `string` | `string`  | `char*`    | `String`  | `string`   |

All the numbers are stored as little-endian in the buffer, if that matters for you. (C types are using `stdint.h` and `stdbool.h`.)


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

For the most part, Beschi tries to keep behavior and structures consistent across the languages, but there are a few points of difference [outlined in detail below](#caveats). Notice in the example above, for instance, that in TypeScript you have to make a call to `Math.fround` if you want to do a straight comparison of float values because of how the underlying JavaScript engine treats all numbers as double-width floats. (Doing equality comparisons on floats is usually a bad idea, but in this instance we *want* to check that they are actually bitwise identical.) Similarly, see how the data members are upper-cased in Go to match that language's export conventions, and the byte reading function is part of the namespace because Go doesn't have static functions for data types. The goal is to make working across languages feel as seamless as possible, but there are some differences that we adapt to as much as possible. 

There are more extensive examples in [the test harnesses](https://github.com/sjml/beschi/tree/main/test/_harnesses).

## Message objects

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

C:
```c
AppMessages_Vector3Message vec3 = AppMessages_Vector3Message_default;
vec3.x = 1.0f;
vec3.y = 2.0f;
vec3.z = 3.0f;

// or
AppMessages_Vector3Message* vec3ptr = malloc(sizeof(AppMessages_Vector3Message));
vec3ptr->x = 1.0f;
vec3ptr->y = 2.0f;
vec3ptr->z = 3.0f;
```

Note that all data members are initialized to zero values (or empty strings/lists). There's no way, at present, to specify other defaults in a protocol, so that needs to be handled in client code. 

(In the function signature pseudocodes below, [...] indicates that specific languages may need additional parameters; these are the bases that indicate broad functionality.)

Instances of the Message base class (interface in Go) defines three methods: 
* `GetMessageType()`: returns an enum value that identifies what specific type of message the object represents
* `GetSizeInBytes()`: returns the size of memory buffer required to write out the message in its current form. If the message and its data members don't contain strings or lists, this is pre-calculated and constant. Otherwise, though, it has to run some calculations to measure out string length, number of items in a list, etc. 
* `WriteBytes(buffer, tag, [...])`: takes the language's equivalent of a data buffer and a boolean value to indicate whether to tag the written data by writing the identifier (from `GetMessageType()`) in front of it. 

Each namespace (or generated file) contains a function for handling a buffer containing multiple messages:
* `ProcessRawBytes(buffer, [...])`: takes a buffer and returns a list/array of Message objects. The messages in the buffer need to be tagged with their identifiers. Note that if it encounters a stretch of memory that it cannot parse, it will append a nil value and stop processing, returning the set of messages parsed so far. 

Each Message class also has a static function in languages that allow it:
* `FromBytes(buffer, [...])`: returns a message of the class's type, or a null value if it could not be parsed. This is useful if you already know what kind of message you're expecting from a certain buffer and don't need to identify it beforehand. 

Note that generated struct objects also have `WriteBytes` and `FromBytes` equivalents, but they need to be used with a little more caution since they throw exceptions (or panic) on errors where Messages will just return a null value if there's a problem.

## Caveats

Beschi is a little bit fast and loose with how it does generation. This allows for simpler generator code (each language writer is around just 400 lines of fairly readable declarative code without layers of templates) and necessitates fewer dependencies (only TOML so far!), but it does mean that there are some situations it can't handle. 

### General
* I make no claims that the produced code is optimal or necessarily even good. It passes a test suite, and I've used it "in production" for personal projects; it seems to work pretty well, but I'm not an expert programmer in all the generated languages, so am very open to feedback if there's something that could be improved. 
* It makes efforts to follow the best practices of each language as much as possible, but the generated code probably won't win any awards from the linters. 
* It always produces *valid* code (if it does not, that is a bug), but it may not be formatted to your (or gofmt's) liking. If you have strong opinions on that sort of thing, consider running it through a code formatter program after generation.
* Makes no attempt to limit variable names other than disallowing whitespace. That means you could name a data member something that is a reserved word in a target language and it would cause compilation problems. If you call a message member "int" you won't be happy, so don't do that; stay happy.
* There are probably some protocols you can define that produce invalid code in the target languages. I'm thinking specifically of some pathological cases of a bunch of nested structs where all data members are called the same thing. So don't do that either. 
* You cannot at present define more than 255 message types in a single namespace. This is because the identifier tag is a single byte. This hasn't proven to be a limitation for me so far, and it could obviously be expanded if needed. 
* Strings and lists use an unsigned 32-bit integer to record their lengths in the buffers. That's enough for more than 4 GB of ASCII text in a string; if you need more, you probably outgrew this system long ago.
* There is no effort made at checking data integrity or the like. It would not be too hard to add a checksum message or data member and perform that verification in client code, though. 
* There is no partial deserialization, like with FlatBuffers, where you can just snag a specific piece of data out of the buffer. I mostly work with small messages that I always want to fully decode, so this was just added overhead; if that's something you need, consider other options. 
* There is no functionality for versioning messages, so if you update your protocol, messages generated from the older code will not be readable by new code. Beschi messages are not intended to persist beyond the time it takes to shuttle them across a network or memory pipe. Versioning can be accomplished on the client side, but will require manual decoding steps and probably retaining the old generated code.

### Go
* Usually the identifying enum is accessed by `{namespace}.MessageType.{specific_message_name}Type`, but Go doesn't do enums the way the other languages do, so it's missing the `.MessageType.` in the middle. 
* The generated Go code uses the standard binary readers and writers, which allow for dealing with whole structures in one go. They seem to pack and unpack identically to the more detailed systems that the other languages need, but there might be some edge cases where packing becomes an issue. 
* Go doesn't have static functions, so instead of `AppMessages.Vector3Message.FromBytes()`, you call `AppMessages.Vector3MessageFromBytes()`. (Note the missing `.` before `FromBytes`.)
* The various `*FromBytes` functions *on structs* also take a pointer to a variable of the appropriate Message type, which will get filled in as it reads. (For messages, you just pass a buffer and it either returns a pointer to the correct type or `nil`.)
* As mentioned above, generated Go code will have all the data members changed to start with an uppercase letter to match the language's export rules. 

### TypeScript
* Following [current recommendations from the TypeScript team](https://www.typescriptlang.org/docs/handbook/namespaces-and-modules.html), it ignores the defined namespace in favor of treating the whole exported code file as a module. You can still get the same syntax by importing like: `import * as AppMessages from './AppMessages';`. 
* The generated TypeScript code uses decorators to provide something similar to static functions. There might be a better way of handling this, and I'm open to suggestion, but for now you have to have `experimentalDecorators` enabled in your TypeScript configuration. 
* 64-bit integers (both signed and unsigned) are implemented with BigInt, which has [pretty broad support at this point](https://caniuse.com/?search=bigint). Your client code may need to handle them differently though -- you can't seamlessly do math with a regular `number` and a `bigint`. Users of other languages are used to these kinds of folds, but JavaScript/TypeScript users may find them new and annoying. :) 
* The generated `WriteBytes()` function for TypeScript takes an additional `offset: number` parameter. Since JavaScript doesn't keep track of a position when writing into a buffer, we have to manually tell it where to start writing. The function also returns a new offset letting you know where it finished writing. 
* Similarly, the TypeScript implementation of `ProcessRawBytes` also takes an offset parameter, and instead of just returning a list of Messages, returns an object: `{ vals: Message[], offset: number }`.
* `FromBytes` also takes an offset and returns a structure similar to the one from `ProcessRawBytes`: `{ val: SpecificMessageType, offset: number }`

### C#
* No particular caveats, actually! Perhaps a side effect of C# being the first generator that was made for this system is that its semantics match up pretty well. 

### Swift
* Swift support is kind of experimental. It's difficult to deal with bytes directly in Swift, so there are some tricky/unsafe things going on to, for example allow unaligned reads in the loading. 
* There might be some extraneous memory copies happening, particularly during writing a message to a buffer. It's actually a little hard to track, but maybe it's ok? Anyway, something to keep awareness of. 
* Swift doesn't have namespaces, and the accepted community practice seems to be wrapping everything in an empty enum. For the most part this makes the code look similar to the other languages, but there is some small weirdness like the `Message` base protocol being prepended with `{namespace}_` rather than being actually inside of it. 

### C
* Unsurprisingly, C code that uses Beschi messages tends to be much more verbose than code from more modern languages. The syntax is a bit different, too, because of the lack of multiple return values and exceptions in C. 
    - Nearly all functions require you to pass in pointers to your objects, and return a `{namespace}_err_t` that you should check is equal to `{NAMESPACE}_ERR_OK` before you use those objects. 
    - Take a look at the test harnesses to see how it works, in general. 
* As always, C makes it far easier to mess things up if you don't pay close attention. Feed the wrong kind of data to a function and it will *try* to recover gracefully and return an error, but it's also just as likely that you'll crash. 
* There's a lot of variants of C, and the generated code is not tested across all of them. It makes the following assumptions:
    - A C99 compiler (makes use of variable declaration in loops and designated initializers)
    - IEEE-754 floating point numbers (a pretty safe assumption, but if you're running on some exotic hardware, this might fail)
    - Little-endian processor (a less safe assumption, but in general is ok; would like to fix this at some point anyway)
* The generated code tries to be as straightforward as possible, so it shouldn't be terribly hard to debug if there's a problem with it. The only macro is a simple error check. 
* C doesn't support any kind of namespacing other than prefixing functions/structs/variables with a string, so that's what the generated code does. You may want to use a shorter namespace string if you're planning to use C code, so as to save some horizontal space in your code editor. 
* The code generated is an [STB-style](https://github.com/nothings/stb/) single-file header library. If you've never used one before, it's actually pretty simple. You `#include "MyGeneratedFile.h"` wherever you need to use the structures and functions, like you normally would with a library. But instead of having a separate file to compile, all the implementation is in the same file, just behind a definition guard. So to actually link the implementation code, in **exactly** one file, `#define {NAMESPACE}_IMPLEMENTATION` **before** you include it. 
* The layout of the structs (mostly) mirrors the way they are declared in the protocol file, which may raise warnings about padding if you compile with warnings all the way up. If memory alignment is important to you, you may want to play with the declaration order. 
    - Exceptions are: 
        - Every message struct has an additional byte (`_mt`) at the start, used to identify it if its in a `void**` array. 
        - Every string and list have an associated `{varname}_len` variable storing their length, right before them in the array. 
        - Lists of strings have a second variable of `{varname}_els_len` recording the lengths of each element in the array. 
        - You probably shouldn't declare members in the protocol that would shadow these variables, but I'm not the boss of you. 
* With the various length variables: they will be set properly when reading a message out of a buffer, but *you are responsible* for making sure they are correct before they go into a buffer. C has no way to track the length of arrays (without introducing another dependency), so it's up to you. 
* The calculated length for strings should *not* include the null terminator. 
* When declaring an instance of a message, it's probably best to use the generated constant `{namespace}_{message_name}_default` to make sure that its members are initialized and that its identifying byte is set correctly. Otherwise things might break. 
* Reading a message from a buffer copies all the data it needs, so the buffer can be discarded safely afterwards. This *does* mean, though, that the reading functions might allocate memory if there are lists or strings in the structure. They will need to be `free`-ed or will leak. 
    - Every message struct has an associated `{namespace}_Destroy{message_type}` function that handles that for you. 
* `ProcessRawBytes` fills an array of pointers to `void` (`void**`), so you need to pass it a *pointer* to such an array, a `void***`. I know, I know. Anyway, once it's filled, you can check each one for its type with `{namespace}_GetMessageType` and then cast as you need to. (There is also a `{namespace}_DestroyMessageList` to help with cleaning that up when you're done.)


## Future
I will admit that part of me wants to make new writers, but since I don't have a separate project motivating that at the moment, it's not likely to get done. If someone loves this system, though, and really wants to see a generator for Rust or Haskell or whatever, let me know. The existing writers should be decent starting points — they aren't terribly clever (no AST or interesting data structures), just iterating over the protocol and writing out serialization/deserialization code. 


## Beschi?
[Constanzo Giuseppe Beschi](https://en.wikipedia.org/wiki/Constanzo_Beschi) was an Italian Jesuit who worked in southern India during the early 18th century. He was noted as a talented linguist, able to tie concepts from multiple languages into a single form. At the same time, he was adept at the Jesuit principle of "inculturation," where foreign concepts are adapted for a new culture and the foreigner attempting the adaptation also respectfully adopts habits and ways of proceeding from the host culture.

