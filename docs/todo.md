* functionality
    - pie in the sky: instead of using int32 for list/string sizes, do an arbitrary-precision thing? (most lists/strings are small)
        - what kind of performance hit does that entail? is it worth the space tradeoff?
        - maybe default to uint16 and have "longString" or long lists? eeeeh, gets complicated fast

* testing framework
    - comparison (size/perf) to flatbuffers/capnproto/etc?
        - I'm willing to bet that beschi will lose in performance, but hopefully not by much. There should be a noticeable win in buffer size, though. Enough to justify this project? Eeeeeeh? 
        - And if it's behind in both memory size AND performance, I still like the client-code ergonomics, so maybe not a total loss. 
    - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
        - qemu or something?
        - how many yaks can be shaved in this project?

* more writers
    * python
    * C
    * swift?
    * rust?
