This file is a rough todo list for the tool itself.

## dustoff notes
- check documentation to make sure it's not promising to be exception-free 
- is `list_size_type` actually implemented?

## Zig writer 
- <sigh> buckle up
- test with a protocol that has no simple structs/messages
- documentation and example file

## protocol features:
- static values, so you can, say, version a message and it will be automatically written to every instance of it
    - maybe like:
        ```toml
        [[structs]]
        _name = "ConfigurationParamaters"
        versionNumber = "u16:24"
        signature = "string:Kilroy was here"
        semver = "[u16]:[0, 1, 0]" # this one makes me nervous for some reason
        defaultColor = "Color:{r: 12, g: 128, b: 255}" # ok, now it's ridiculous
        # ..."
        ```
    - proposal:
        - statics are allowed for numeric types (and lists of numeric types) only
        - statics cannot be set from target language; will be overwritten with static value when put into the buffer
            - note that this might lead to leaked memory or trashed pointers if you're not careful in C
- inline string and array length types so they don't have to be protocol-wide like they are now
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

## "immediate" todo
- make multiple message stream a bit smarter (below)
- docstrings in various languages?
- add "IsValid" function to languages where it makes sense:
    - check that numbers are in the appropriate range (like JavaScript where everything is everything)
        - in languages with strong types enforced by a compiler, skip
    - check that strings and lists are <= their max defined length
- add optional bounds checking on buffer access
  - zig: 
    ```zig
    if (config.bounds_checking) {
        if (offset + @sizeOf(T) >= buffer.len) {
            @panic(std.fmt.comptimePrint("Writing {s} outside of buffer bounds", .{@typeName(T)}));
        }
    }
    ```

## functionality
- can size limits on arrays be enforced? at least when writing?
- open question: should the multiple message format (as read by ProcessRawBytes) be a little smarter?
    - right now is very minimal
    - but maybe could also have a little header: 
        - first four bytes are number of messages
        - next set of four bytes each are the length of each message
        - (or should the length of each message come right before it? is this an arbitrary distinction or are there performance/usability tradeoffs?)
        - could even do checksums or something in here if needed
        - *then* the messages themselves
    - should be an associated PackMessages function that takes a list of messages and makes these bytes from it

## testing framework
  - comparison (size/perf) to flatbuffers/capnproto/etc?
      - I'm willing to bet that beschi will lose in performance, but hopefully not by much. There should be a noticeable win in buffer size, though. Enough to justify this project? Eeeeeeh? 
      - And if it's behind in both memory size AND performance, I still like the client-code ergonomics, so maybe not a total loss. 
  - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
      - qemu or something?
      - how many yaks can be shaved in this project?
      - (would need to add endian-awareness to C if so)

## more writers
* python
* java?
* lua?
