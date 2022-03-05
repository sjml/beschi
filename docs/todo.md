* immediate todo
    - make multiple message stream a bit smarter (below)
    - redo docs
        - revamp readme, move separate language out to own files
        - make note that getsizeinbytes returns whatever the language does for their equivalent of size_t

* functionality
    - pie in the sky: instead of using int32 for list/string sizes, do an arbitrary-precision thing? (most lists/strings are small)
        - what kind of performance hit does that entail? is it worth the space tradeoff?
        - maybe default to uint16 and have "longString" or long lists? eeeeh, gets complicated fast
    - open question: should the multiple message format (as read by ProcessRawBytes) be a little smarter?
        - right now is very minimal
        - but maybe could also have a little header: 
            - first four bytes are number of messages
            - next set of four bytes each are the length of each message
            - (or should the length of each message come right before it? is this an arbitrary distinction or are there performance/usability tradeoffs?)
            - could even do checksums or something in here if needed
            - *then* the messages themselves
        - should be an associated PackMessages function that takes a list of messages and makes these bytes from it
    - language-specific flags
        - thoughts on renaming... priorities go as follows:
            - creating code that works out of the box with no warnings in target language
            - creating code that works out of the box in target language (so you should be able to access the data members of a message, for instance)
            - THEN principle of least surprise (so only renaming things by default if they would cause warnings)
            - otherwise, rename requires active request (--csharp-rename-members)
            - automatic renames can be supressed if people want (--rust-no-rename)

* testing framework
    - check that multiple generated files can be included at once
    - test uninitialized message
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
    * lua?
