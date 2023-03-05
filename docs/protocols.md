# Beschi Protocols

Protocols are described in [TOML](https://toml.io) files. In general, if a file describes a protocol that cannot be generated, it should fail before anything is output and return an error code. If you manage to construct a protocol that produces invalid output, please file a bug. 


## Meta section

Example:
```toml
[meta]
namespace = "AppMessages"
list_size_type = "uint16"
string_size_type = "byte"
```

The entire meta section is optional; if nothing is specified there are reasonable defaults. 

* `namespace` (optional, but very much recommended): Not every target language does something useful with this value, but it can be very handy for avoiding name clashes either with existing code or other Beschi-generated files. 
* `list_size_type`: By default, lists record their lengths into the buffers using a 32-bit unsigned integer. That's enough for 4 billion entries, which may be overkill. You can specify another integral type here if you want to save some bytes. (Alternately, you could crank it up to `uint64` and have up to 18 quintillion entries...)
* `string_size_type`: Similar to the `list_size_type`, but applies for encoding the length of strings. The default can store over 4GB of text, so that's probably enough, but if you know your strings are always short, you can take this down to `byte` and save space in your buffer.

**IMPORTANT NOTE**: The size limits are *not* enforced in the generated code. They are a promise you make to the system, not a law you are laying down. If you say that list sizes can be stored in a byte, but then try to store a list with 300 values, behavior is undefined; each generated language fails in different ways. 


## Structs

Example:
```toml
[[structs]]
_name = "Color"
red = "float"
green = "float"
blue = "float"

[[structs]]
_name = "PlayerData"
id = "uint16"
nickname = "string"
teamColor = "Color"
finishedTutorial = "bool"
strength = "byte"
intelligence = "byte"
gold = "uint64"
friends = "[uint16]"
```

Structs help you organize your data. You specify them in the `[[structs]]` table. (This double bracket is standard TOML syntax — basically each time you specify a section that way, you are making a new entry in the table called "`structs`.")

Each struct needs to have a `_name` value that will be used to make native structures in the generated code. Every other entry in the table is a piece of data that is part of the struct. 


### Base Types

The following are the base data types that everything else is built from: 

| Protocol Data Type | Meaning |
|--------------------|---------|
| `byte`             | An unsigned 8-bit integer (0 - 255). Stored in one byte. |
| `bool`             | A boolean value (true/false). Stored in one byte. |
| `uint16`           | An unsigned 16-bit integer (0 - 65,535). Stored in two bytes. |
| `int16`            | A signed 16-bit integer (-32,768 - 32,767). Stored in two bytes. |
| `uint32`           | An unsigned 32-bit integer (0 - 4,294,967,295). Stored in four bytes. |
| `int32`            | A signed 32-bit integer (-2,147,483,648 - 2,147,483,647). Stored in four bytes. |
| `uint64`           | An unsigned 64-bit integer (0 - 18,446,744,073,709,551,615). Stored in eight bytes. |
| `int64`            | A signed 64-bit integer (-9,223,372,036,854,775,808 - 9,223,372,036,854,775,807). Stored in eight bytes. |
| `float`            | A single precision [IEEE-754 floating point number](https://en.wikipedia.org/wiki/IEEE_754). Stored in four bytes. |
| `double`           | A double precision [IEEE-754 floating point number](https://en.wikipedia.org/wiki/IEEE_754). Stored in eight bytes.
| `string`           | A variable-length set of bytes representing [UTF-8 encoded](https://en.wikipedia.org/wiki/UTF-8) text. Stored as an integer (by default, a `uint32`) representing the length, and then the bytes themselves. |


### Lists

You can specify that a data member is a list of values by enclosing the type in brackets like so: `[uint64]`. This will get translated to whatever list or array functionality the target language has. You can also have lists of structs like `[Color]` so there is a lot of room to express many different kinds of data. 


## Messages

Specifying messages is done the same way we describe structs; the only difference is that they get added to a separate table. 

Example:
```toml
[[messages]]
_name = "PlayerJoinedGame"
id = "uint16"
newNickname = "string"
teamColors = "[Color]"
```

Messages are indeed very similar to structs, but there are a few important distinctions: 
* Messages can contain base types, structs, and lists of either. Structs can contain other structs, but messages *cannot* contain other messages. 
* Only messages are written and read to buffers. (There are generated functions that do similarly with structs, but they should be considered internal implementation details and not called directly.)

In short, messages are usually what you want to be operating on, but structs are very handy ways to bunch a group of data together for organiational purproses.

Note that all data members are initialized to zero values (or empty strings/lists). There's no way, at present, to specify other defaults in a protocol, so that needs to be handled in client code. 


## Invalid Protocols

Certain protocols will throw errors and not output any generated code. The rules are pretty minimal and, I think, somewhat self-evident. 

* Every data member must be either a base type, a struct, a list of base types, or a list of structs. Anything else will fail. 
* Namespaces, struct names, message names, and data member names cannot contain any spaces.
* Structs and messages must always have a `_name` property.
* Struct and message names must be unique. 
* Struct names, message names, and data member names cannot be the same as any of the base types (or `list` or `string`). 
* You cannot have circular references (struct A contains a list of struct B, which contains a struct A).
* `list_size_type` and `string_size_type`, if specified, must refer to integral types. (One of `byte`, `uint16`, `int16`, `uint32`, `int32`, `uint64`, or `int64`)
* Lists cannot be directly nested, so you can't create a list of lists of floats with `[[float]]`, but you *could* create a struct that contains a single float and make a list of that. 
* You cannot have more than 255 message types in a single protocol. 

(This last point is because the MessageType identifier is represented with a single byte; in practice I have not found this to be a limitation, but it could be easily expanded if need be.)
