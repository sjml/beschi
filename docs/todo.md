* functionality
    - pie in the sky: instead of using int32 for list/string sizes, do an arbitrary-precision thing? (most lists/strings are small)
        - what kind of performance hit does that entail? is it worth the space tradeoff?
        - maybe default to uint16 and have "longString" or long lists? eeeeh, gets complicated fast

* testing framework
    - comparison (size/perf) to flatbuffers/capnproto/etc?
    - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
        - qemu or something?
        - how many yaks can be shaved in this project?

* more writers
    * python
    * C
    * swift?
    * rust?
