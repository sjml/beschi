# Using Beschi with Zig

(You can see [an example Zig file](../generated_examples/zig_example.ts) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/zig/).) 


## Data Types

The base data types map to Zig accordingly: 

| Protocol Type | Zig type |
|---------------|---------------|
| `byte`        | `u8`          |
| `bool`        | `bool`        |
| `int16`       | `i16`         |
| `uint16`      | `u16`         |
| `int32`       | `i32`         |
| `uint32`      | `u32`         |
| `int64`       | `i64`         |
| `uint64`      | `u64`         |
| `float`       | `f32`         |
| `double`      | `f64`         |
| `string`      | `[] const u8` |


## Caveats

* Similar to [TypeScript](./typescript.md#caveats), it ignores the defined namespace in favor of treating the whole exported code file as a struct. This is the generally accepted practice in the Zig community; basically everything is namespaced per-file by default. 
* Similar to [Rust](./rust.md#caveats), since Zig doesn't have inheritance, Messages are defined as a union wrapping an enum. This really only comes into play when you're reading a message stream with `processRawBytes` and it wants to give you an array of something like a base class. You can switch on `Message` to get the actual instance. ([The testing code gives an example here.](../../test/_harnesses/zig/src/multiple.zig))
    * Note that this means every message takes up as much memory as the largest message. Shouldn't be a problem unless you have a huge range of message sizes, but if you are particularly memory concious, here's something to watch out for. 

