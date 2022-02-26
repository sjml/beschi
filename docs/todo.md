* functionality
    - pie in the sky: instead of using int32 for list/string sizes, do an arbitrary-precision thing? (most lists/strings are small)
        - what kind of performance hit does that entail? is it worth the space tradeoff?
        - maybe default to uint16 and have "longString" or long lists? eeeeh, gets complicated fast
    - typescript: wrap the read/writes in a class that tracks file position so client code doesn't have to manage the offset (put into boilerplate)
        - c# and go may also benefit from boilerplate

* generator cleanup
    - some leftover code from way back when
        - label.endswith is used kind of awkwardly
        - "list" type not used at all
    - messages are really just structs with some extra things; could probably streamline a lot of operations by consolidating them and having a flag

* testing framework
    - check that multiple generated files can be included at once
    - test that C code compiles and works from C++
    - make pathological protocol (multiple nested lists of things) to make sure serializer/deserializer generation handles indexing properly
    - add a POD list to basic
    - comparison (size/perf) to flatbuffers/capnproto/etc?
        - I'm willing to bet that beschi will lose in performance, but hopefully not by much. There should be a noticeable win in buffer size, though. Enough to justify this project? Eeeeeeh? 
        - And if it's behind in both memory size AND performance, I still like the client-code ergonomics, so maybe not a total loss. 
    - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
        - qemu or something?
        - how many yaks can be shaved in this project?

* more writers
    * python
    * java?
    * rust?
