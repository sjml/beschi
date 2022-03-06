# Using Beschi with C#

(You can see [an example C# file](../generated_examples/csharp_example.cs) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/csharp/).)


## Data Types

The base data types map to C# accordingly: 

| Protocol Type | C# type  |
|---------------|----------|
| `byte`        | `byte`   |
| `bool`        | `bool`   |
| `int16`       | `short`  |
| `uint16`      | `ushort` |
| `int32`       | `int`    |
| `uint32`      | `uint`   |
| `int64`       | `long`   |
| `uint64`      | `ulong`  |
| `float`       | `float`  |
| `double`      | `double` |
| `string`      | `string` |

If you describe a list in your protocol, it will be mapped to a `List<{type}>` on the C# side. 


## Caveats

* No particular caveats, actually! Perhaps a side effect of C# being the first generator that was made for Beschi is that its semantics match up pretty well. 
