# Using Beschi with Go

(You can see [an example Go file](../generated_examples/go_example.go) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/go/).)


## Data Types

The base data types map to Go accordingly: 

| Protocol Type | Go type   |
|---------------|-----------|
| `byte`        | `byte`    |
| `bool`        | `bool`    |
| `int16`       | `int16`   |
| `uint16`      | `uint16`  |
| `int32`       | `int32`   |
| `uint32`      | `uint32`  |
| `int64`       | `int64`   |
| `uint64`      | `uint64`  |
| `float`       | `float32` |
| `double`      | `float64` |
| `string`      | `string`  |


## Caveats

* Usually the identifying enum is accessed by `{namespace}.MessageType.{specific_message_name}Type`, but Go doesn't do enums the way the other languages do, so it's missing the `.MessageType.` in the middle. 
* The generated Go code uses the standard binary readers and writers, which allow for dealing with whole structures in one go. They seem to pack and unpack identically to the more detailed systems that the other languages need, but there might be some edge cases where packing becomes an issue. 
* Go doesn't have static functions, so instead of `AppMessages.Vector3Message.FromBytes()`, you call `AppMessages.Vector3MessageFromBytes()`. (Note the missing `.` before `FromBytes`.)
* The various `*FromBytes` functions *on structs* also take a pointer to a variable of the appropriate Message type, which will get filled in as it reads. (For messages, you just pass a buffer and it either returns a pointer to the correct type or `nil`.)
* Data members are automatically renamed to Uppercase because otherwise they will not be accessible to client code. To suppress this renaming, pass `--go-no-rename` on the command line.
* If you don't specify a value on a Go struct, it is set to zero. Most of the time this makes sense, **except** for the case where you've created a non-sequential enum that has no zero value. In that case, the enum, rather than being set to the same default as in the other languages (the first value listed in the protocol), it will be set to an invalid number. To get a default that matches the other languages, use the `New{MyStructOrMessage}Default` functions. 
