This file is a rough todo list for the tool itself.

## "immediate" todo
* TypeScript -- code for converting to and from POJO
* Zig -- update to latest Zig

## possible future protocol features:
- ?? inline string and array length types so they don't have to be protocol-wide like they are now
    - not pressing, but worth thinking of
        ```toml
        [[structs]]
        _name = "BunchaCollections"
        shorty = "string[u8]"
        medium = "string[u16]"
        gargantuan = "string[u64]"
        regular = "string[]" # will use the default
        regular2 = "string" # will also use the default
        smallList = "[f32][u8]"
        universe = "[f64][u64]"
        regList = "[DataType][]" # default
        regList2 = "[DataType]" # default
        ```
    - I still like this idea in the larger sense; feels like a very pragmatic thing to have. In current projects though I'm not quibbling over a few bytes, and the effort of implementing and testing this across all generated languages would be high.

## horizon
- should Rust have a BufferedWriter that takes either a `[u8]` or a `Vec<u8>`?
- add endian handling to C writer for the sake of completeness
- add zig cc / zig c++ as compiler for c tests
  - musl build on linux?
  - also check on windows
  - maybe do debug and release builds for languages where it makes sense
- test suite for destroying and cleaning up messages
- add notes about trustworthiness
  - all reading code assumes it's reading stuff that was written by a corresponding writer
  - no security checks
  - do not use on untrusted input
- add "IsValid" function to languages where it makes sense:
    - check that numbers are in the appropriate range (like JavaScript where everything is everything)
        - in languages with strong types enforced by a compiler, skip
    - check that strings and lists are <= their max defined length
    - check that enums actually match one of the values
- add optional bounds checking on buffer access
  - zig: 
    ```zig
    if (config.bounds_checking) {
        if (offset + @sizeOf(T) >= buffer.len) {
            @panic(std.fmt.comptimePrint("Writing {s} outside of buffer bounds", .{@typeName(T)}));
        }
    }
    ```

## testing framework
  - comparison (size/perf) to flatbuffers/capnproto/etc?
      - I'm willing to bet that beschi will lose in performance, but hopefully not by much. There should be at lest a small win in buffer size, though. Enough to justify this project? Eeeeeeh? 
      - And if it's behind in both memory size AND performance, I still like the client-code ergonomics, so maybe not a total loss. 
  - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
      - qemu or something?
      - how many yaks can be shaved in this project?
      - (would need to add endian-awareness to C if so)

## more writers
* python
* java?
* lua?
