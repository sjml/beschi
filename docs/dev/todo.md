This file is a rough todo list for the tool itself.

## dustoff notes
- actually, go back to appending null to broken message stream
    - useful for saying "we found something we didn't recognize"
    - BUT also create a pack message function and have ProcessRawBytes take a max value
    - procedure:
      - change ProcessRawBytes back to appending null
        - takes a max value (signed int32)
          - if 0, return empty list
          - if negative, consider infinite
      - update multiple_broken and multiple tests
      - GetPackedSize
      - PackMessages
        - writes BSCI
        - write 4 bytes: u32 number of messages
        - write all messages (tagged)
        - write null byte
      - UnpackMessages
        - ensures header: "Packed message buffer has invalid header."
        - gets message count
        - runs processraw
        - if 0 messages read, throw: "No messages in buffer."
        - if last message is null, discard it
        - if count is off, throw: "Unexpected number of messages in buffer."
      - packed test
        - pack a variety of messages
        - check them as they come out
    - done for:
      - ✅ C#
      - ✅ TypeScript
      - ✅ Go
      - ⬜️ Swift
      - ✅ Rust
      - ✅ Zig
      - ✅ C
    - update documentation before publishing 0.3.*
        - call out that process_raw_bytes doesn't append null in Rust
            - that this was an ergonomics decision (otherwise having to deal with vec of optionals), but can be revisited
        - if you call from_bytes on a generic message, it has to be tagged
    - UnpackMessages should check for EOF on reads and throw/return errors as appropriate
        - make sure we're consuming the terminator, too
- add endian handling to C writer for the sake of completion
- add zig cc / zig c++ as compiler for c tests
  - musl build on linux?
  - also check on windows
  - maybe do debug and release builds for languages where it makes sense
- test suite for destroying and cleaning up messages
- add notes about trustworthiness
  - all reading code assumes it's reading stuff that was written by a corresponding writer
  - no security checks
  - do not use on untrusted input

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

## "immediate" todo
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
