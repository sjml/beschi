This file is a rough todo list for the tool itself.

* dustoff notes
  - check documentation to make sure it's not promising to be exception-free 

* Zig writer 
  - <sigh> buckle up

* "immediate" todo
    - make multiple message stream a bit smarter (below)
    - docstrings in various languages?
    - add "IsValid" function to languages where it makes sense:
        - check that numbers are in the appropriate range (like JavaScript where everything is everything)
            - in languages with strong types enforced by a compiler, skip
        - check that strings and lists are <= their max defined length

* functionality
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

* testing framework
    - comparison (size/perf) to flatbuffers/capnproto/etc?
        - I'm willing to bet that beschi will lose in performance, but hopefully not by much. There should be a noticeable win in buffer size, though. Enough to justify this project? Eeeeeeh? 
        - And if it's behind in both memory size AND performance, I still like the client-code ergonomics, so maybe not a total loss. 
    - is there some way to test it with big-endian architecture too so we can be sure it's consistent? 
        - qemu or something?
        - how many yaks can be shaved in this project?
        - (would need to add endian-awareness to C if so)

* more writers
    * python
    * java?
    * lua?
