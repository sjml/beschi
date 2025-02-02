# Using Beschi with TypeScript

(You can see [an example TypeScript file](../generated_examples/typescript_example.ts) generated from [this annotated protocol](../../test/_protocols/annotated.toml). Example code can be found in [the test harnesses directory](../../test/_harnesses/typescript/).) 


## Data Types

The base data types map to TypeScript accordingly: 

| Protocol Type | TypeScript type |
|---------------|-----------------|
| `byte`        | `number`        |
| `bool`        | `boolean`       |
| `int16`       | `number`        |
| `uint16`      | `number`        |
| `int32`       | `number`        |
| `uint32`      | `number`        |
| `int64`       | `bigint`        |
| `uint64`      | `bigint`        |
| `float`       | `number`        |
| `double`      | `number`        |
| `string`      | `string`        |


## Caveats

* Following [current recommendations from the TypeScript team](https://www.typescriptlang.org/docs/handbook/namespaces-and-modules.html), it ignores the defined namespace in favor of treating the whole exported code file as a module. You can still get the same syntax by importing like: `import * as AppMessages from './AppMessages';`. 
    * If you truly need the namespace for some reason, just pass `--typescript-use-namespace` on the command line.
* 64-bit integers (both signed and unsigned) are implemented with [BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt), which has [pretty broad support at this point](https://caniuse.com/?search=bigint). Your client code may need to handle them differently though -- you can't seamlessly do math with a regular `number` and a `bigint`. Users of other languages are used to these kinds of folds, but JavaScript/TypeScript users may find them new and annoying. :) 
* Reading and writing messages is wrapped in a custom `DataAccess` class that tracks position in a `DataView`. You can either construct it yourself if you want to, for instance, do multiple passes of writing to the same buffer. If you pass a `DataView` to a function that expects a `DataAccess`, the latter will be used internally but not returned to you. 
    * Be careful of long-lasting `DataView` (and thus `DataAccess`) objects, though, since they become invalid if their underlying `ArrayBuffer` gets detached. Usually you're aware of that happening, but if you're working with a WebAssembly module's memory, it happens whenever the memory grows (which you might **not** be aware of). You can always just make a new `DataView` object from the memory when that happens, though. (Documenting here because I was bitten by it myself!)
