# Using Beschi with Swift

(You can see [an example Swift file](../generated_examples/swift_example.swift) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/swift/).)


## Data Types

The base data types map to Swift accordingly: 

| Protocol Type | Swift type |
|---------------|------------|
| `byte`        | `UInt8`    |
| `bool`        | `Bool`     |
| `int16`       | `Int16`    |
| `uint16`      | `UInt16`   |
| `int32`       | `Int32`    |
| `uint32`      | `UInt32`   |
| `int64`       | `Int64`    |
| `uint64`      | `UInt64`   |
| `float`       | `Float32`  |
| `double`      | `Float64`  |
| `string`      | `String`   |


## Caveats

* It's difficult to deal with bytes directly in Swift, so there are some tricky/unsafe things going on to, for example allow unaligned reads in the loading. 
* There might be some extraneous memory copies happening, particularly during writing a message to a buffer. It's actually a little hard to track, but maybe it's ok? Anyway, something to keep awareness of. 
* Swift doesn't have namespaces, and the accepted community practice seems to be wrapping everything in an empty enum. For the most part this makes the code look similar to the other languages, but there is some small weirdness like the `Message` base protocol being prepended with `{namespace}_` rather than being actually inside of it. 
* Reading and writing messages is wrapped in custom `DataReader` and `DataWriter` classes that track position in one of the built-in `Data` objects. You can either construct it yourself if you want to, for instance, do multiple passes of writing to the same buffer. If you pass a `Data` to a function that expects a `Data{Reader|Writer}`, the latter will be used internally but not returned to you. 
