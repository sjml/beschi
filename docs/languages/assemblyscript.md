# Using Beschi with AssemblyScript

(You can see [an example AssemblyScript file](../generated_examples/assemblyscript_example.ts) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/assemblyscript/).) 


## Data Types

The base data types map to AssemblyScript accordingly: 

| Protocol Type | AssemblyScript type |
|---------------|---------------------|
| `byte`        | `u8`                |
| `bool`        | `bool`              |
| `int16`       | `i16`               |
| `uint16`      | `u16`               |
| `int32`       | `i32`               |
| `uint32`      | `u32`               |
| `int64`       | `i64`               |
| `uint64`      | `u64`               |
| `float`       | `f32`               |
| `double`      | `f64`               |
| `string`      | `string`            |


## Caveats

* [AssemblyScript](https://www.assemblyscript.org/) is a bit of a strange beast. I had expected it to be "a strongly-typed subset of TypeScript that compiles to WebAssembly" but it turns out it's closer to "C, but with TypeScript syntax and a bunch of convenience functions." That's not a bad thing to be, at all, but it just took me a little by surprise. 
    * The AssemblyScript generator is implemented as a bunch of modifications to the TypeScript generator. Knowing the above now, I probably would have written it from scratch. But it works now, so it stays until I get frustrated with it. 
    * In fairness to AssemblyScript, its self-description is "A TypeScript-like language for WebAssembly" so it's being pretty honest about the value proposition. 
* In particular, AssemblyScript lacks exceptions in any kind of recoverable way; so Beschi-generated code does not throw when it encounters a problem. If possible (like in the `writeBytes` functions), it returns a bool indicating success or failure. Reading messages might return `null`. An out-of-range enum, instead of throwing an exception, will be set to a value of `_Unknown`. 
    * The only exceptions (hehe) to this are anything dealing with PackedMessage -- if you're trying to unpack a buffer that doesn't have the right header, or miscounts the number of messages or something, there's no real good way to recover from that anyway. 
* While it passes the test suite, this is probably the least mature and least tested-in-a-real-setting of the supported languages. 
