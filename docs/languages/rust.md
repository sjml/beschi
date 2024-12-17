# Using Beschi with Rust

(You can see [an example Rust file](../generated_examples/rust_example.rs) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/rust/).)


## Data Types

The base data types map to Rust accordingly: 

| Protocol Type | Rust type |
|---------------|-----------|
| `byte`        | `u8`      |
| `bool`        | `bool`    |
| `int16`       | `i16`     |
| `uint16`      | `u16`     |
| `int32`       | `i32`     |
| `uint32`      | `u32`     |
| `int64`       | `i64`     |
| `uint64`      | `u64`     |
| `float`       | `f32`     |
| `double`      | `f64`     |
| `string`      | `String`  |


## Caveats

* Beschi does its best to generate code that feels at home in the target languages, which means the Rust version has some different semantics. 
* Messages are defined as an enum with data, so instead of having to examine and cast them, you use Rust's usual pattern-matching to figure out what kind of message structure you're looking at. 
    * Note that this means every message takes up as much memory as the largest message. Shouldn't be a problem unless you have a huge range of message sizes, but if you are particularly memory concious, here's something to watch out for. 
    * Because of the way the enum is set up, you can call the static `from_bytes` on `Message` itself isntead of a one of the specific message types; the only caveat is that if you do so it expects a buffer that starts with the tag of the message type.
* The generated code shouldn't raise warnings from the standard compiler... but `clippy` is another matter. Most of the warnings I've seen are things that can be changed by altering the protocol (for example, all members of an enum having the same suffix). So if you want `clippy` to be happy, be ready to either suppress some warnings or tinker with your protocol. 
* Data members are automatically renamed to snake_case because otherwise the Rust compiler will throw warnings. To suppress this renaming, pass `--rust-no-rename` on the command line.
